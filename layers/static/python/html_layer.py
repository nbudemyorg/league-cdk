home_page = """
<!DOCTYPE html>
<html>
<head>
    <title>League Home</title>
</head>
<body>
    <h1>FC26</h1>
</body>
</html>
"""

access_denied = """
<!DOCTYPE html>
<html>
<head>
    <title>Access Denied</title>
</head>
<body>
    <h1>Access Denied</h1>
</body>
</html>
"""

server_error = """
<!DOCTYPE html>
<html>
<head>
    <title>Access Denied</title>
</head>
<body>
    <h1>Access Denied</h1>
</body>
</html>
"""

login_form = """
<form action="/prod/login" method="post">
  <label for="player_id">PlayerId:</label>
  <input type="text" id="player_id" name="player_id" required>

  <label for="password">Password:</label>
  <input type="password" id="password" name="password" required>

  <button type="submit">Login</button>
</form>
"""

registration_form = """
<form action="/prod/register" method="post">
  <label for="player_id">PlayerId:</label>
  <input type="text" id="player_id" name="player_id" required>

  <label for="password">Password:</label>
  <input type="password" id="password" name="password" required>

  <label for="email">Email:</label>
  <input type="text" id="email" name="email" required>

  <label for="invite">Invite Key:</label>
  <input type="password" id="invite" name="invite" required>

  <button type="submit">Submit</button>
</form>
"""
