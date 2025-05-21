DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nome_do_banco',      # nome do banco existente
        'USER': 'usuario',
        'PASSWORD': 'senha',
        'HOST': '5432',          # ou IP/host do container Docker
        'PORT': '5432',
    }
}
