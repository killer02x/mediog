from django.db.models import Avg, FloatField
from django import template
from django.utils.safestring import mark_safe
from diagnosis.models import Rating
from django.db.models.functions import Coalesce


register = template.Library()

@register.simple_tag
def get_doctor_rating(doctor_pk):
    average_rating = Rating.objects.filter(doctor=doctor_pk).aggregate(average_rating=Avg('rating', output_field=FloatField()))
    return average_rating['average_rating'] if average_rating['average_rating'] is not None else 0

@register.simple_tag
def render_stars(doctor_pk):
    rating = get_doctor_rating(doctor_pk)
    stars = ''
    for i in range(5):  # Предполагаем, что максимальный рейтинг - 5
        if i < rating:
            stars += '<i class="fas fa-star filled"></i>'
        else:
            stars += '<i class="fas fa-star"></i>'
    return mark_safe(stars)

@register.simple_tag
def render_stars_for_detail_page(rating):
    stars = ''
    for i in range(5):  # Предполагаем, что максимальный рейтинг - 5
        if i < rating:
            stars += '<i class="fas fa-star filled"></i>'
        else:
            stars += '<i class="fas fa-star"></i>'
    return mark_safe(stars)

@register.simple_tag
def get_doctor_reviews_count(doctor_pk):
    return Rating.objects.filter(doctor=doctor_pk).count()




