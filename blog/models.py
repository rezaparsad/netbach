from django.db import models

from account.models import User
from main.media_model import Media


class Category(models.Model):
    reply = None

    user = models.ForeignKey(User, models.PROTECT, related_name='blog_category_user')
    reply_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=150)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    view = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # seo
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=150, null=True, blank=True)
    keywords = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    image_meta = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='blog_category_imagemeta', null=True, blank=True)

    def __str__(self):
        return self.name

    def get_reply(self):
        if self.reply_id:
            try:
                self.reply = Category.objects.get(pk=self.reply_id)
                return ''
            except Exception:
                return None

    def increase_view(self, amount=1):
        self.view += amount
        self.save()


class Blog(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    category = models.ManyToManyField(Category, blank=True)
    name = models.CharField(max_length=150)
    content = models.TextField()
    poster = models.ForeignKey(Media, on_delete=models.CASCADE, related_name="blog_blog_poster")
    is_active = models.BooleanField(default=True)
    view = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # seo
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=150, null=True, blank=True)
    keywords = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    image_meta = models.ForeignKey(Media, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        blogs = Blog.objects.all()
        try:
            blogs.get(pk=self.pk)
            if blogs.filter(slug=self.slug).exclude(pk=self.pk).count() > 0 and len(blogs) != 0:
                self.slug += "-" + str(Blog.objects.last().pk + 1)
        except Exception:
            if not self.slug:
                self.slug = self.name.replace('/', '-').replace(' ', '-')

            if blogs.filter(slug=self.slug).count() > 0 and len(blogs) != 0:
                self.slug += "-" + str(Blog.objects.last().pk + 1)
        super(Blog, self).save(*args, **kwargs)

    def increase_view(self, amount=1):
        self.view += amount
        self.save()

    def submit_vote(self, user, blog, answer=True):
        try:
            vote = ReviewRating(user=user)
            vote.answer = answer
            vote.save()
        except Exception:
            vote = ReviewRating.objects.create(user=user, blog=blog, answer=answer)
            self.save()

    def get_starts(self):
        reviews = ReviewRating.objects.filter(blog__pk=self.pk)
        if len(reviews) == 0:
            return 0
        return (len(reviews.filter(answer=True)) / len(reviews) * 100) // 20

    def get_percentage(self):
        reviews = ReviewRating.objects.filter(blog__pk=self.pk)
        return (len(reviews.filter(answer=True)) / len(reviews) * 100) / 20
    

class ReviewRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    blog = models.ForeignKey(Blog, models.CASCADE)
    answer = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
