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
    username = models.CharField(max_length=64)
    email = models.EmailField(null=False, blank=False, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def get_user_by_email(email):
        try:
            return User.objects.get(email=email)
        except Exception:
            return None