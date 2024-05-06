# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from pytils.translit import slugify
from uuid import uuid4
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator


def article_directory_path(instance, filename):
    return "user_{0}/{1}/{2}".format(instance.author.id, instance.id, filename)


def validate_pdf_file(file):
    if file.name.split('.')[-1].lower() != "pdf":
        raise ValidationError("Разрешены только PDF файлы.")
    return file


class Account(AbstractUser):
    READER = 1
    AUTHOR = 2
    ROOT = 3

    ROLE_CHOICES = (
        (READER, 'Reader'),
        (AUTHOR, 'Author'),
        (ROOT, 'Root'),
    )

    username_validator = UnicodeUsernameValidator()

    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES,
                                            default=1)
    email = models.EmailField('Электронная почта', unique=True)
    username = models.CharField('Имя пользователя', unique=True,
                                max_length=150,
                                validators=[username_validator],
                                error_messages={
                                    "unique": _(
                                        "A user with that username already \
exists."),
                                }, )
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    third_name = models.CharField('Отчество', max_length=150, blank=True,
                                  null=True)
    fullname = models.CharField(max_length=452)

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        self.fullname = f"{self.last_name} {self.first_name} \
{self.third_name}" if self.third_name else f"{self.last_name} \
{self.first_name}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Аккаунт'
        verbose_name_plural = 'Аккаунты'


class Article(models.Model):
    title = models.CharField('Название статьи', max_length=128)
    abstract = models.TextField('Аннотация к статье', null=True)
    date_created = models.DateTimeField('Дата создания', auto_now_add=True)
    views = models.PositiveIntegerField('Количество просмотров', default=0)
    downloads = models.PositiveIntegerField('Количество загрузок', default=0)
    author = models.ForeignKey(Account, on_delete=models.CASCADE)
    article = models.FileField('Статья', upload_to=article_directory_path,
                               validators=[validate_pdf_file])
    keywords = models.JSONField(
        default=list, null=True,
        blank=True)
    # если вдруг траблы, то юзать нижнее
    # keywords = models.TextField(default='')
    # def get_keyword_list(self):
    #     return self.keywords.split(',')
    # def set_keyword_list(self, keyword_list):
    #     self.keywords = ','.join(keyword_list)
    slug = models.SlugField(max_length=255, db_index=True, verbose_name="URL",
                            blank=True, editable=False)
    is_active = models.BooleanField('Статус', default=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.slug == '':
            self.slug = slugify(
                f'{self.title}-b\
y-{self.author.fullname}--{uuid4().hex[:4]}')
            while Article.objects.filter(slug=self.slug).exists():
                self.slug = slugify(
                    f'{self.title}-b\
y-{self.author.fullname}--{uuid4().hex[:4]}')
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
