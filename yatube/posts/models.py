from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

NUMBER_OF_CHARACTERS: int = 15


class Post(models.Model):
    text = models.TextField(
        'Текст поста',
        help_text='Текст нового поста',
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
    )
    # labels = {
    #     'group': 'Группа'
    # }
    # help_texts = {
    #     'group': 'Группа, к которой будет относиться пост'
    # }

    group = models.ForeignKey(
        'Group',
        on_delete=models.CASCADE,
        max_length=None,
        blank=True,
        null=True,
        related_name='posts',
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:NUMBER_OF_CHARACTERS]


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=40, unique=True)
    description = models.TextField(max_length=None)

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField(
        'Текст',
        help_text='Текст нового комментария'
    )