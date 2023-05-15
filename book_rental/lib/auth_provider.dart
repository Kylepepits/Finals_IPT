import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

class User {
  final String username;
  final String accessToken;
  final String? refreshToken;

  User({
    required this.username,
    required this.accessToken,
    this.refreshToken,
  });
}

class AuthProvider with ChangeNotifier {
  User? _user;

  User? get user => _user;
  String? get username => _user?.username;
  String? get accessToken => _user?.accessToken;
  String? get refreshToken => _user?.refreshToken;

  Future<void> login(String username, String password) async {
    final response = await http.post(
      Uri.parse('http://127.0.0.1:8000/api/login/'),
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
      body: jsonEncode(<String, String>{
        'username': username,
        'password': password,
      }),
    );

    if (response.statusCode == 200) {
      final responseData = jsonDecode(response.body);
      final username = responseData['user_data']?['username'];
      final accessToken = responseData['access_token'];
      final refreshToken = responseData['refresh_token'];

      if (username != null && accessToken != null && refreshToken != null) {
        _user = User(
            username: username,
            accessToken: accessToken,
            refreshToken: refreshToken);
        notifyListeners();
      } else {
        throw Exception('Failed to get user data');
      }
    } else {
      throw Exception('Failed to login');
    }
  }

  Future<void> logout() async {
    final response = await http.post(
      Uri.parse('http://127.0.0.1:8000/api/logout/'),
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization':
            'Bearer ${_user?.accessToken}', // access accessToken from AuthProvider
      },
      body: jsonEncode(<String, String>{
        'refresh_token':
            _user?.refreshToken ?? '', // access refreshToken from AuthProvider
      }),
    );

    if (response.statusCode == 200) {
      _user = null;
      notifyListeners();
    } else {
      throw Exception('Failed to logout');
    }
  }
}
