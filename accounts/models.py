from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin

class UserManager(BaseUserManager):    
    
    use_in_migrations = True    
    
    def create_user(self, username, email, password=None):        
        
        if not username :
            raise ValueError('Username is required.')   
            
        if not email :            
            raise ValueError('Email is required.') 
       
        user = self.model(      
            username = username,      
            email = self.normalize_email(email),            
        )
        if password:
            user.set_password(password)
                           
        user.save(using=self._db)        
        return user    
     
    def create_superuser(self, username, email, password):        
       
        user = self.create_user(
            username = username,
            email = self.normalize_email(email),            
            password = password           
        )           
        user.is_superuser = True
        user.is_admin = True     
        user.is_staff = True        
        user.save(using=self._db)        
        return user 

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=64, blank=True, null=True)
    email = models.EmailField(null=False, blank=False, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    
    def get_user_by_email(email):
        try:
            return User.objects.get(email=email)
        except Exception:
            return None
    
    def extract_user_data_by_provider(provider, data):
        if provider == 'google':
            return {
                'username': data.get('name', None),
                'email': data.get('email', None)
            }
        elif provider == 'kakao':
            return {
                'username': data['kakao_account']['profile']['nickname'],
                'email': data['kakao_account']['email'],
            }
        else:
            raise ValueError("Unsupported provider.")