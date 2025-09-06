from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from quiz.models import SkinProfile
from faker import Faker
import random
from django.utils import timezone
import time

class Command(BaseCommand):
    help = 'Create 500 random users with SkinProfile'
    
    def handle(self, *args, **kwargs):
        start = time.time()

        fake = Faker()
        NUM_USERS = 500
        
        for i in range(NUM_USERS):
            while True:
                username = fake.user_name()
                if not User.objects.filter(username=username).exists():
                    break

            while True:
                email = fake.email()
                if not User.objects.filter(email=email).exists():
                    break

            password = 'password1234'

            user = User.objects.create_user(username=username, email=email, password=password)

            skin_profile, created = SkinProfile.objects.get_or_create(
                user=user,
                defaults={
                    'quiz_completd': True,
                    'quiz_skipped': True,
                    'completed_at': timezone.now(),
                    'skin_type': random.choice(['dry', 'oily', 'sensitive', 'combination', 'normal']),
                    'acne': random.randint(-5, 5),
                    'dryness': random.randint(-5, 5),
                    'sensitivity': random.randint(-5, 5),
                    'oiliness': random.randint(-5, 5),
                    'redness': random.randint(-5, 5),
                    'hydration': random.randint(-5, 5),
                    'elasticity': random.randint(-5, 5),
                }
            )

            if not created:
                skin_profile.quiz_completed = True
                skin_profile.quiz_skipped = True
                skin_profile.completed_at = timezone.now()
                k = random.randint(5, 12) // 5
                skin_profile.skin_type = random.choices(['dry', 'oily', 'sensitive', 'combination', 'normal'], k=k)
                skin_profile.acne = random.randint(-5, 5)
                skin_profile.dryness = random.randint(-5, 5)
                skin_profile.sensitivity = random.randint(-5, 5)
                skin_profile.oiliness = random.randint(-5, 5)
                skin_profile.redness = random.randint(-5, 5)
                skin_profile.hydration = random.randint(-5, 5)
                skin_profile.elasticity = random.randint(-5, 5)
                skin_profile.save()
            
            self.stdout.write(self.style.SUCCESS(f'{username} and its SkinProfile created successfully!'))
            self.stdout.write(self.style.SUCCESS(f'{i + 1} users created till now'))

        end = time.time()
        self.stdout.write(self.style.SUCCESS(f'{NUM_USERS} users and SkinProfiles created successfully in {(end - start):.2f} seconds!'))
