python setup.py sdist
for /f %%i in ('dir /b dist\automotive*.tar.gz') do (
set filename=%%i
)
python -m pip install dist\%filename%