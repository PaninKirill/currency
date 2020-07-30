from settings.handler_views import error_400, error_500


def test_error_handlers(mocker):
    request = mocker.patch('requests.get')
    response = error_500(request)
    assert response.status_code == 500

    request = mocker.patch('requests.get')
    response = error_400(request)
    assert response.status_code == 400
