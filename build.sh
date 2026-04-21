# #!/usr/bin/env bash
# pip install -r requirements.txt
# python manage.py collectstatic --noinput
# python manage.py migrate

#!/usr/bin/env bash

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate