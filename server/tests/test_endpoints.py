def test_read_main(client):
    response = client.get("/api/sms")
    assert response.status_code == 200
