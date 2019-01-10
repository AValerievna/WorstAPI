def get_key(fixt, setup_api_worker):
    """
    :return key of user, noticed in fixt
    """
    (username, password) = fixt
    api_worker = setup_api_worker

    pub_key = api_worker.request_pubkey().text
    private_key = api_worker.request_login(username, password, pub_key).text
    return private_key
