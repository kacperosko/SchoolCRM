from .views_base import *


@check_permission('crm.view_location')
def all_locations(request):
    locations_records = None
    try:
        locations_records = Location.objects.all()
    except Exception as e:
        custom_404(request, e)

    return render(request, 'crm/locations.html', {'locations': locations_records})


@check_permission('crm.view_location')
def view_location(request, location_id):
    context = {}
    if not location_id:
        return custom_404(request, "Nieprawidłowy id lokalizacji")

    tab_name = request.GET.get("tab", "Details")
    if not request.GET._mutable:
        request.GET._mutable = True

    request.GET['tab'] = tab_name
    try:
        location = Location.objects.get(id=location_id)
        try:
            model_name = get_model_by_prefix(location.id[:3])
            user_watch_record = WatchRecord.objects.get(user=request.user, content_type__model=model_name.lower(),
                                                        object_id=location_id)
        except WatchRecord.DoesNotExist:
            user_watch_record = None

        notes = location.notes.all()
        context['notes'] = notes.order_by('-created_at')
        context['watch_record'] = user_watch_record
        context['record'] = location

    except ObjectDoesNotExist:
        messages.error(request, 'Nie znaleziono takiego rekordu')
        return redirect('/location')
    except Exception as e:
        return custom_404(request, e)

    return render(request, 'crm/location-page.html', context)