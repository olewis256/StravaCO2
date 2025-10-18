"""
Defines the endpoints available (i.e. the valid paths that users can make requests to),
and their responses.
"""

from . import app
from flask import Response, render_template, request, redirect

import strava_api as api
from . import units


def render_error(code: int):
    refresh = request.cookies.get('refresh-token')
    return render_template('error.html', title=f'Error {code}', connect_url=api.connect_url, auth=bool(refresh), code=code)


@app.route('/')
def home():
    client = api.Client.from_refresh(request.cookies.get('refresh-token'))
    if not client:
        # The user hasn't authorized, delete stored token (if exists) and render home
        res = Response(render_template('home/index.html', title='Home', connect_url=api.connect_url, auth=False))
        res.delete_cookie('refresh-token')
        return res

    athlete = api.get_athlete(client)
    if isinstance(athlete, api.models.Fault): return render_error(500)
    activity_stats = api.get_athlete_stats(client, athlete.id)
    if isinstance(activity_stats, api.models.Fault): return render_error(500)

    use_metric = athlete.measurement_preference == 'meters'

    res = render_template(
        'profile/index.html',
        title='Home',
        connect_url=api.connect_url,
        auth=True,
        sport=request.args.get('sport', default='', type=str),
        # Tell the template how to format distances and elevations
        format_distance=lambda x: units.format_distance(x, use_metric),
        format_elevation=lambda x: units.format_elevation(x, use_metric),
        format_time=units.format_time,
        # Athlete info
        athlete=athlete,
        stats=activity_stats,
    )
    print(f"Responded to '{request.path}' with {client.api_calls} API calls")
    return res


@app.route('/about')
def about():
    refresh = request.cookies.get('refresh-token')
    return render_template('about/index.html', title='About', connect_url=api.connect_url, auth=bool(refresh))


@app.route('/authorize')
def authorize():
    # We have an authorization request from Strava
    error = request.args.get('error')
    if error:
        return error

    client = api.Client.from_code(request.args.get('code'))
    if not client:
        return "Failed to authenticate"

    # Set the refresh token as a cookie on the client
    res = redirect('/')
    res.set_cookie('refresh-token', client.tokens.refresh, httponly=True, max_age=2592000)

    return res


@app.route('/deauthorize')
def deauthorize():
    # The user wants to log out
    client = api.Client.from_refresh(request.cookies.get('refresh-token'))
    if client: client.deauthorize()
    res = redirect('/')
    res.delete_cookie('refresh-token')
    return res

@app.route('/co2')
def CO2():
    refresh = request.cookies.get('refresh-token')
    client = api.Client.from_refresh(request.cookies.get('refresh-token'))
    if not client:
        # The user hasn't authorized, delete stored token (if exists) and render home
        res = Response(render_template('home/index.html', title='Home', connect_url=api.connect_url, auth=False))
        res.delete_cookie('refresh-token')
        return res

    athlete = api.get_athlete(client)
    if isinstance(athlete, api.models.Fault): return render_error(500)
    activity_stats = api.get_athlete_stats(client, athlete.id)
    if isinstance(activity_stats, api.models.Fault): return render_error(500)

    use_metric = athlete.measurement_preference == 'meters'

    dist_ride = activity_stats.all_ride_totals.distance
    dist_run = activity_stats.all_run_totals.distance

    emission_run_car = api.Emissions.emissions(distance=dist_run, type='car')
    emission_bike_car = api.Emissions.emissions(distance=dist_ride, type='car')

    emission_run_train = api.Emissions.emissions(distance=dist_run, type='train')
    emission_bike_train = api.Emissions.emissions(distance=dist_ride, type='train')

    emission_run_car = units.format_emissions(emission_run_car)
    emission_bike_car = units.format_emissions(emission_bike_car)

    emission_run_train = units.format_emissions(emission_run_train)
    emission_bike_train = units.format_emissions(emission_bike_train)

    res = render_template('co2/index.html',
                            title='CO2',
                            athlete=athlete,
                            auth=bool(refresh),
                            co2_running_car=emission_run_car,
                            co2_riding_car=emission_bike_car,
                            co2_running_train=emission_run_train,
                            co2_riding_train=emission_bike_train)

    return res
