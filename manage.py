# gerencia o site
#!/usr/bin/env python

"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()


# verificar o no terminal está na pasta "D:\PycharmProjects\ecommerce_site_quadros\ecommerce"
# se não tiver desse modo aplicar o comando "cd D:\PycharmProjects\ecommerce_site_quadros\ecommerce"
# depois aplicar no terminal o codigo "python manage.py runserver"
# recomeçar na aula 27 se não funcionar
