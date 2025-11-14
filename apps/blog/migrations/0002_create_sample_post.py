from django.db import migrations


def create_sample_post(apps, schema_editor):
    from django.utils import timezone

    Post = apps.get_model('blog', 'Post')
    Category = apps.get_model('blog', 'Category')

    cat, _ = Category.objects.get_or_create(name='Announcements', slug='announcements')

    if not Post.objects.filter(slug='welcome-to-uh-care').exists():
        Post.objects.create(
            title='Welcome to UH Care',
            slug='welcome-to-uh-care',
            author=None,
            excerpt='Welcome to the UH Care blog. Here you will find product updates, health tips, and company news.',
            content='''<p>Welcome to the UH Care blog — we're glad you're here. This space will contain updates about our services, practical home healthcare tips, and stories from our providers.</p>
<p>Stay tuned for regular posts, and contact us if you'd like to contribute or suggest topics.</p>''',
            category=cat,
            status='published',
            published_at=timezone.now(),
        )


def remove_sample_post(apps, schema_editor):
    Post = apps.get_model('blog', 'Post')
    Post.objects.filter(slug='welcome-to-uh-care').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_sample_post, remove_sample_post),
    ]
