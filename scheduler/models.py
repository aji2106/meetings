from django.db import models
from scheduler.utils.functions import get_first_letters_of_active_days


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
