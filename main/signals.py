from constance.signals import config_updated
from django.db.models import Q
from django.dispatch import receiver

from dragonstone import models, PVM, SKILLING, MAJOR, OTHER, EVENT_MENTOR
from main import EASY, MEDIUM, HARD, VERY_HARD

__all__ = ["constance_updated"]


@receiver(config_updated)
def constance_updated(sender, key, old_value, new_value, **kwargs):
    objects_mapping = {
        "RECRUITER_PTS": models.RecruitmentPoints.objects.all(),
        "SOTM_FIRST_PTS": models.SotMPoints.objects.filter(rank=1),
        "SOTM_SECOND_PTS": models.SotMPoints.objects.filter(rank=2),
        "SOTM_THIRD_PTS": models.SotMPoints.objects.filter(rank=3),
        "PVM_SPLITS_EASY_PTS": models.PVMSplitPoints.objects.filter(
            submission__content__difficulty=EASY
        ),
        "PVM_SPLITS_MEDIUM_PTS": models.PVMSplitPoints.objects.filter(
            submission__content__difficulty=MEDIUM
        ),
        "PVM_SPLITS_HARD_PTS": models.PVMSplitPoints.objects.filter(
            submission__content__difficulty=HARD
        ),
        "PVM_SPLITS_VERY_HARD_PTS": models.PVMSplitPoints.objects.filter(
            submission__content__difficulty=VERY_HARD
        ),
        "MENTOR_EASY_PTS": models.MentorPoints.objects.filter(
            submission__content__difficulty=EASY
        ),
        "MENTOR_MEDIUM_PTS": models.MentorPoints.objects.filter(
            submission__content__difficulty=MEDIUM
        ),
        "MENTOR_HARD_PTS": models.MentorPoints.objects.filter(
            submission__content__difficulty=HARD
        ),
        "MENTOR_VERY_HARD_PTS": models.MentorPoints.objects.filter(
            submission__content__difficulty=VERY_HARD
        ),
        "EVENT_MINOR_HOSTS_PTS": models.EventHostPoints.objects.filter(
            Q(submission__type=PVM) | Q(submission__type=SKILLING)
        ),
        "EVENT_MINOR_PARTICIPANTS_PTS": models.EventParticipantPoints.objects.filter(
            Q(submission__type=PVM) | Q(submission__type=SKILLING)
        ),
        "EVENT_MINOR_DONORS_PTS": models.EventDonorPoints.objects.filter(
            Q(submission__type=PVM) | Q(submission__type=SKILLING)
        ),
        "EVENT_MENTOR_HOSTS_PTS": models.EventHostPoints.objects.filter(
            submission__type=EVENT_MENTOR
        ),
        "EVENT_MENTOR_PARTICIPANTS_PTS": models.EventParticipantPoints.objects.filter(
            submission__type=EVENT_MENTOR
        ),
        "EVENT_MENTOR_DONORS_PTS": models.EventDonorPoints.objects.filter(
            submission__type=EVENT_MENTOR
        ),
        "EVENT_MAJOR_HOSTS_PTS": models.EventHostPoints.objects.filter(
            submission__type=MAJOR
        ),
        "EVENT_MAJOR_PARTICIPANTS_PTS": models.EventParticipantPoints.objects.filter(
            submission__type=MAJOR
        ),
        "EVENT_MAJOR_DONORS_PTS": models.EventDonorPoints.objects.filter(
            submission__type=MAJOR
        ),
        "EVENT_OTHER_HOSTS_PTS": models.EventHostPoints.objects.filter(
            submission__type=OTHER
        ),
        "EVENT_OTHER_PARTICIPANTS_PTS": models.EventParticipantPoints.objects.filter(
            submission__type=OTHER
        ),
        "EVENT_OTHER_DONORS_PTS": models.EventDonorPoints.objects.filter(
            submission__type=OTHER
        ),
    }
    if key in objects_mapping.keys():
        objects_mapping[key].update(points=new_value)
