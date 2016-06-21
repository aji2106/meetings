from django.db import models
from scheduler.utils.functions import get_first_letters_of_active_days
from django.utils import timezone


class Schedule(models.Model):
    """Stores data about time spans and weekdays in which meetings can be scheduled"""
    start_time = models.TimeField()
    end_time = models.TimeField()
    days = models.IntegerField()  # Sum of bit values of selected days (Monday=1..Wednesday=4..Sunday=64)

    def __str__(self):
        return 'on %s from %s to %s' % (
            get_first_letters_of_active_days(self.days),
            self.start_time.strftime("%H:%M"),
            self.end_time.strftime("%H:%M")
        )

    @staticmethod
    def get_active_model(start_hour=7, end_hour=17, days=31):
        """Get the only Schedule model instance (or create one if it doesn't exist yet)"""
        schedule = Schedule.objects.order_by('-pk').first()
        if not schedule:
            schedule = Schedule(
                start_time=timezone.datetime(1, 1, 1, start_hour, 0, 0).time(),
                end_time=timezone.datetime(1, 1, 1, end_hour, 0, 0).time(),
                days=days
            )
            schedule.save()
        return schedule


class Meeting(models.Model):
    """Stores time and date of a meeting"""
    start_time = models.TimeField()
    end_time = models.TimeField()
    date = models.DateField()

    def __str__(self):
        return 'on %s from %s to %s' % (
            self.date.strftime("%d.%m.%Y"),
            self.start_time.strftime("%H:%M"),
            self.end_time.strftime("%H:%M")
        )
