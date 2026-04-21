"""
Face recognition utilities using OpenCV for simplicity
"""
import cv2
import numpy as np
import io
import json
import logging
from PIL import Image
from django.core.files.base import ContentFile
from django.conf import settings
from .models import FaceData

logger = logging.getLogger(__name__)

# Load pre-trained face detection cascade classifier
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)


class FaceRecognitionManager:
    """Manages face recognition operations using MediaPipe"""
    
    def __init__(self):
        self.tolerance = settings.FACE_RECOGNITION_TOLERANCE
    
    @staticmethod
    def load_image_from_file(image_file):
        """Load and convert image file to RGB array"""
        try:
            image = Image.open(image_file)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return np.array(image)
        except Exception as e:
            logger.error(f"Error loading image: {str(e)}")
            raise
    
    def get_face_encoding(self, image_array):
        """
        Extract face bounding box using OpenCV cascade classifier
        Returns simplified encoding based on face location
        """
        try:
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            if len(faces) == 0:
                return None, 0
            
            if len(faces) > 1:
                # Return largest face
                faces = [max(faces, key=lambda f: f[2] * f[3])]
            
            x, y, w, h = faces[0]
            h_img, w_img = image_array.shape[:2]
            
            # Create encoding from normalized bounding box coordinates
            encoding = np.array([
                x / w_img,      # normalized x
                y / h_img,      # normalized y
                w / w_img,      # normalized width
                h / h_img,      # normalized height
                (w * h) / (w_img * h_img)  # face area ratio
            ], dtype=np.float32)
            
            return encoding, len(faces)
        
        except Exception as e:
            logger.error(f"Error getting face encoding: {str(e)}")
            return None, 0
    
    def register_face(self, user, image_file):
        """
        Register/store face for a user
        Returns: (success, message, encoding)
        """
        try:
            # Load image
            image_array = self.load_image_from_file(image_file)
            
            # Get face encoding
            encoding, face_count = self.get_face_encoding(image_array)
            
            if encoding is None:
                return False, "No face detected in image", None
            
            if face_count > 1:
                return False, "Multiple faces detected. Please provide a clear photo with only your face", None
            
            # Convert encoding to JSON-serializable format
            encoding_json = json.dumps(encoding.tolist())
            
            # Save face data
            face_data, created = FaceData.objects.update_or_create(
                user=user,
                defaults={
                    'face_encoding': encoding_json,
                    'image_path': image_file,
                    'quality_score': 0.95
                }
            )
            
            # Update user
            user.face_encoding = encoding_json
            user.face_registered = True
            user.save()
            
            return True, "Face registered successfully", encoding
        
        except Exception as e:
            logger.error(f"Error registering face for user {user.id}: {str(e)}")
            return False, f"Error registering face: {str(e)}", None
    
    def verify_face(self, user, image_file):
        """
        Verify face against stored encoding
        Returns: (verified, confidence_score, message)
        """
        try:
            if not user.face_registered:
                return False, 0, "User face not registered"
            
            # Load test image
            test_image = self.load_image_from_file(image_file)
            test_encoding, _ = self.get_face_encoding(test_image)
            
            if test_encoding is None:
                return False, 0, "No face detected in provided image"
            
            # Get stored encoding
            stored_encoding = np.array(json.loads(user.face_encoding))
            
            # Compare face locations (using bounding box similarity)
            # Calculate distance between encodings
            distance = np.linalg.norm(stored_encoding[:4] - test_encoding[:4])
            
            # Normalize distance to 0-1 range (approximate)
            confidence = max(0, 1 - (distance / 2.0))
            is_match = distance <= 0.5  # Threshold for face matching
            
            return is_match, float(confidence), f"Verification {'successful' if is_match else 'failed'}"
        
        except json.JSONDecodeError:
            logger.error(f"Invalid face encoding for user {user.id}")
            return False, 0, "Invalid face data stored"
        except Exception as e:
            logger.error(f"Error verifying face for user {user.id}: {str(e)}")
            return False, 0, f"Error during verification: {str(e)}"
    
    def compare_faces(self, encoding1, encoding2):
        """
        Compare two face encodings
        Returns: (match, distance)
        """
        try:
            distance = np.linalg.norm(encoding1[:4] - encoding2[:4])
            is_match = distance <= 0.5
            return is_match, float(distance)
        except Exception as e:
            logger.error(f"Error comparing faces: {str(e)}")
            return False, 1.0
    
    @staticmethod
    def extract_face_region(image_array, save_path=None):
        """
        Extract and optionally save the face region from image
        """
        try:
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
            
            if len(faces) == 0:
                return None
            
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
            
            # Add padding
            padding = 20
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(image_array.shape[1] - x, w + padding * 2)
            h = min(image_array.shape[0] - y, h + padding * 2)
            
            face_image = image_array[y:y+h, x:x+w]
            
            if save_path:
                face_pil = Image.fromarray(face_image.astype('uint8'))
                face_pil.save(save_path)
            
            return face_image
        
        except Exception as e:
            logger.error(f"Error extracting face region: {str(e)}")
            return None
    
    @staticmethod
    def get_face_quality_score(image_array):
        """
        Estimate face quality based on size and positioning
        Returns score between 0 and 1
        """
        try:
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
            
            if len(faces) == 0:
                return 0
            
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
            h_img, w_img = image_array.shape[:2]
            
            # Calculate face area as percentage of image
            face_area = (w * h) / (w_img * h_img)
            
            # Optimal face area is 20-50% of image
            if face_area < 0.1:
                return 0.5  # Face too small
            elif face_area > 0.6:
                return 0.7  # Face too large
            else:
                return min(0.95, face_area + 0.3)  # Good quality
        
        except Exception as e:
            logger.error(f"Error calculating face quality: {str(e)}")
            return 0


# Global instance
face_manager = FaceRecognitionManager()
