from django.core.urlresolvers import reverse
from django.shortcuts import HttpResponseRedirect, get_object_or_404, render
from django.utils import timezone
from .models import Meeting, Schedule
from .utils.functions import get_active_days_indices, get_active_days_names, days_bit


def __render_error_message(_message, _request, _template, _context):
    # Add default values for instructions
    schedule = Schedule.get_active_model()
    _context['schedule'] = schedule
    _context['scheduled_days'] = ', '.join(get_active_days_names(schedule.days, True)) if schedule else ''
    _context['future_meetings'] = Meeting.get_future_meetings(10)
    _context['active_days_indices'] = get_active_days_indices(schedule.days)
    # Add error message
    _context['error_message'] = _message
    return render(_request, _template, _context)


def index(request):
    """Shows on which days and time meeting room is available, plus when the next 10 meetings are scheduled"""
    schedule = Schedule.get_active_model()
    context = {
        'schedule': schedule,
        'scheduled_days': ', '.join(get_active_days_names(schedule.days, True)) if schedule else '',
        'future_meetings': Meeting.get_future_meetings(10)
    }
    return render(request, 'scheduler/index.html', context=context)


def schedule_config(request):
    """Set on which days in week and at which time the meeting room is available to schedule"""
    schedule = Schedule.get_active_model()
    context = {day.lower(): True for day in get_active_days_names(schedule.days)}  # Get all activated days names
    context['schedule'] = schedule
    return render(request, 'scheduler/schedule.html', context=context)


def schedule_save(request):
    """Save Schedule settings"""
    context = request.POST.dict()
    # Check form values
    if not context['start_time']:
        if context['end_time']:
            context['end_time'] = timezone.datetime.strptime(context['end_time'], '%H:%M').time()
        return __render_error_message('You must set "From" time.', request, 'scheduler/schedule.html', context)
    # We have start_time, check for end_time
    context['start_time'] = timezone.datetime.strptime(context['start_time'], '%H:%M').time()  #: save start_time as time
    if not context['end_time']:
        return __render_error_message('You must set "To" time.', request, 'scheduler/schedule.html', context)
    # We also have end_time, make sure there's at least one day selected
    context['end_time'] = timezone.datetime.strptime(context['end_time'], '%H:%M').time()  #: save end_time as time
    # Make sure start_time is before end_time
    if context['start_time'] >= context['end_time']:
        if context['end_time'] != timezone.datetime(1, 1, 1, 0, 0, 0, 0).time():
            # start_time has to be earlier than end_time, or end_time should be '00:00' as midnight
            return __render_error_message('"Start" time has to be earlier than "End" time',
                                          request, 'scheduler/schedule.html', context)
    days_bit_sum = sum([days_bit[day] for day in days_bit if day in context])
    if not days_bit_sum:
        return __render_error_message('You must select at least 1 day.',
                                      request, 'scheduler/schedule.html', context)

    # all passed, lets save data
    schedule = Schedule.get_active_model()  # Creates Schedule on first run

    schedule.start_time = context['start_time']
    schedule.end_time = context['end_time']
    schedule.days = days_bit_sum
    schedule.save()
    return HttpResponseRedirect(reverse('scheduler:index'))


def meeting_config(request):
    """Show empty Meeting form"""
    schedule = Schedule.get_active_model()
    context = {
        'schedule': schedule,
        'scheduled_days': ', '.join(get_active_days_names(schedule.days, True)) if schedule else '',
        'future_meetings': Meeting.get_future_meetings(10),
        'active_days_indices': get_active_days_indices(schedule.days)
    }
    return render(request, 'scheduler/meeting.html', context=context)


def meeting_edit(request, meeting_id):
    """Show form Meeting settings for an existing Meeting model"""
    try:
        schedule = Schedule.get_active_model()
        meeting = get_object_or_404(Meeting, pk=meeting_id)
    except (KeyError, Meeting.DoesNotExist):
        context = {
            'scheduler': Schedule.get_active_model(),
            'meeting': None,
            'error_message': 'Wrong meeting.id',
            'scheduled_days': ', '.join(get_active_days_names(schedule.days, True)) if schedule else '',
            'future_meetings': Meeting.get_future_meetings(10),
            'active_days_indices': get_active_days_indices(schedule.days),
        }
        return render(request, 'scheduler/meeting.html', context=context)
    else:
        schedule = Schedule.get_active_model()
        context = {
            'meeting': meeting,
            'schedule': schedule,
            'scheduled_days': ', '.join(get_active_days_names(schedule.days, True)) if schedule else '',
            'future_meetings': Meeting.get_future_meetings(10),
            'active_days_indices': get_active_days_indices(schedule.days),
        }
        return render(request, 'scheduler/meeting.html', context=context)


def meeting_save(request, meeting_id=None):
    """Update or create new Meeting and save the settings"""
    try:
        context = request.POST.dict()
        schedule = Schedule.get_active_model()
        midnight = timezone.datetime(1, 1, 1, 0, 0, 0, 0).time()
        if meeting_id:
            meeting = get_object_or_404(Meeting, pk=meeting_id)
            context['meeting'] = meeting

        # Check form values
        if not context['start_time']:
            if context['end_time']:
                context['end_time'] = timezone.datetime.strptime(context['end_time'], '%H:%M').time()
            return __render_error_message('You must set "From" time.', request, 'scheduler/meeting.html', context)
        # Save start_time as time
        context['start_time'] = timezone.datetime.strptime(context['start_time'], '%H:%M').time()

        if not context['end_time']:
            return __render_error_message('You must set "To" time.', request, 'scheduler/meeting.html', context)
        # Save end_time as time
        context['end_time'] = timezone.datetime.strptime(context['end_time'], '%H:%M').time()

        if not context['date']:
            return __render_error_message('You must set Date of the meeting', request, 'scheduler/meeting.html', context)
        context['date'] = timezone.datetime.strptime(context['date'], '%d.%m.%Y')

        if context['start_time'] >= context['end_time']:
            if context['end_time'] != midnight:
                # start_time has to be earlier than end_time, or end_time should be '00:00' as midnight
                return __render_error_message('"Start" time has to be earlier than "End" time',
                                              request, 'scheduler/meeting.html', context)

        # Make sure that meeting is scheduled when meeting room is open
        if context['start_time'] < schedule.start_time or context['end_time'] > schedule.end_time:
            if schedule.end_time != midnight:
                return __render_error_message('Scheduled meeting is outside permitted limits',
                                              request, 'scheduler/meeting.html', context)

        # Check if meeting collides with any already scheduled meetings
        meetings = Meeting.objects.filter(date=context['date'])
        if meeting_id:
            # Remove the one we're editing
            meetings = meetings.exclude(pk=meeting_id)

        for mtng in meetings:
            if mtng.start_time < context['start_time'] < mtng.end_time or \
                    mtng.start_time < context['end_time'] < mtng.end_time or \
                    context['start_time'] < mtng.start_time < context['end_time'] or \
                    context['start_time'] < mtng.end_time < context['end_time']:
                return __render_error_message('Scheduled meeting cannot overlap.',
                                              request, 'scheduler/meeting.html', context)

        # OK, Let's save it
        if meeting_id:
            # Update existing
            meeting = get_object_or_404(Meeting, pk=meeting_id)
            meeting.start_time = context['start_time']
            meeting.end_time = context['end_time']
            meeting.date = context['date']
            meeting.save()
        else:
            # Create new
            meeting = Meeting(
                start_time=context['start_time'],
                end_time=context['end_time'],
                date=context['date']
            )
            meeting.save()

    except (KeyError, Meeting.DoesNotExist):
        # Redisplay the question voting form
        return render(request, 'scheduler/index.html', {
            'error_message': 'Meeting does not exist.',
        })

    # Always return an HttpResponseRedirect after successfully dealing with POST data.
    # This prevents data from being posted twice if a user hits the Back button.
    return HttpResponseRedirect(reverse('scheduler:index'))


def meeting_delete(request, meeting_id):
    """Delete a meeting"""
    try:
        meeting = get_object_or_404(Meeting, pk=meeting_id)
    except (KeyError, Meeting.DoesNotExist):
        # Redisplay the question voting form
        return render(request, 'scheduler/meeting.html', {
            'error_message': 'Meeting with id %d, does not exist.' % meeting_id,
        })
    else:
        meeting.delete()
        if not Meeting.objects.filter(pk=meeting_id).first():
            return HttpResponseRedirect(reverse('scheduler:index'))
        else:
            return HttpResponseRedirect(request, 'scheduler/index.html',
                                        context={'error_message': 'Error while deleting meeting'})
