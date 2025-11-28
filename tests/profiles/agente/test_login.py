from tests.pages.login_page import LoginPage

def test_login_agente(page, settings):
    print("TYPE PAGE:", type(page))
    print("RAW PAGE:", page)

    login = LoginPage(page)
    login.open()
    login.login(settings.username, settings.password)

    assert login.is_logged(), "El usuario no logró iniciar sesión correctamente."




