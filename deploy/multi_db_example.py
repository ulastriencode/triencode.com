# --- MULTI-DB CONFIG EXAMPLE ---
# Place this inside your Django settings after importing os.environ, etc.
DATABASES = {
    'default': {  # can be used for shared/public stuff or left minimal
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DEFAULT_DB_NAME', 'portal_default'),
        'USER': os.getenv('DEFAULT_DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DEFAULT_DB_PASSWORD', ''),
        'HOST': os.getenv('DEFAULT_DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DEFAULT_DB_PORT', '5432'),
    },
    'sonerdicanav': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('SONERDICANAV_DB_NAME', 'portal_sonerdicanav'),
        'USER': os.getenv('SONERDICANAV_DB_USER', 'postgres'),
        'PASSWORD': os.getenv('SONERDICANAV_DB_PASSWORD', ''),
        'HOST': os.getenv('SONERDICANAV_DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('SONERDICANAV_DB_PORT', '5432'),
    },
    'emirkevserav': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('EMIRKEVSERAV_DB_NAME', 'portal_emirkevserav'),
        'USER': os.getenv('EMIRKEVSERAV_DB_USER', 'postgres'),
        'PASSWORD': os.getenv('EMIRKEVSERAV_DB_PASSWORD', ''),
        'HOST': os.getenv('EMIRKEVSERAV_DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('EMIRKEVSERAV_DB_PORT', '5432'),
    },
}
