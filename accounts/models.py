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
     
    def create_superuser(self, email, password):        
       
        user = self.create_user(
            username = email.split('@')[0],
            email = self.normalize_email(email),            
            password = password           
        )           
        user.is_superuser = True
        user.is_admin = True     
        user.is_staff = True        
        user.save(using=self._db)        
        return user 

class User(AbstractBaseUser, PermissionsMixin):
    
    LEVELS = (
        ('NEWBIE', '뉴비'),
        ('ROOKIE', '루키'),
        ('SEMIPRO', '세미프로'),
        ('PRO', '프로'),
        ('MASTER', '마스터'),
    )
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=64, blank=True, null=True)
    email = models.EmailField(null=False, blank=False, unique=True)
    provider = models.CharField(max_length=32, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    level = models.CharField(choices=LEVELS, verbose_name='레벨', max_length=8, default='NEWBIE')
    point = models.IntegerField(verbose_name='포인트', default=0)
    manner_score = models.FloatField(verbose_name='매너지수', default=0)
    profile = models.JSONField(verbose_name='프로필사진',null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def update_level(user):
        if 500<= user.point <1500:
            user.level = 'ROOKIE'
        elif 1500<= user.point <3500:
            user.level = 'SEMIPRO'
        elif 3500<= user.point <6000:
            user.level = 'PRO'
        else:
            user.level = 'MASTER'
        user.save()
    
    def update_point(user):
        user.point+=50
        user.save()
    
    def update_manner_score(user):
        from products.models import Review
        from django.db.models import Sum
        reviews = Review.objects.filter(product__owner=user)
        count = reviews.count()

        if count == 0:
            user.manner_score = 0
        else:
            sum = reviews.aggregate(sum=Sum('star'))['sum']
            user.manner_score = round(((sum * 20) / count), 1)
        
        user.save()
        return user
    
    def get_user_by_email(email, provider):
        try:
            return User.objects.get(email=email, provider=provider)
        except Exception:
            return None
    
    def extract_user_data_by_provider(provider, data):
        if provider == 'google':
            return {
                'username': data.get('name', None),
                'email': data.get('email', None),
                'provider' : provider,
            }
        elif provider == 'kakao':
            return {
                'username': data['kakao_account']['profile']['nickname'],
                'email': data['kakao_account']['email'],
                'provider' : provider,
            }
        else:
            raise ValueError("Unsupported provider.")