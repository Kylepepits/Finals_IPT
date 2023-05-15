import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:provider/provider.dart';

import 'auth_provider.dart';

class UserRentedBooksScreen extends StatefulWidget {
  final int userId;

  UserRentedBooksScreen({required this.userId});

  @override
  _UserRentedBooksScreenState createState() => _UserRentedBooksScreenState();
}

class _UserRentedBooksScreenState extends State<UserRentedBooksScreen> {
  late Future<List<dynamic>> _booksFuture;

  @override
  void initState() {
    super.initState();
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final accessToken = authProvider.accessToken;
    _booksFuture = _fetchBooks(accessToken);
  }

  Future<List<dynamic>> _fetchBooks(String? accessToken) async {
    final url = 'http://127.0.0.1:8000/api/users/${widget.userId}/books/';
    final response = await http.get(
      Uri.parse(url),
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer $accessToken',
      },
    );

    if (response.statusCode == 200) {
      final responseData = jsonDecode(response.body);
      return responseData;
    } else {
      throw Exception('Failed to load books');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Books rented by user'),
      ),
      body: FutureBuilder<List<dynamic>>(
        future: _booksFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.done) {
            if (snapshot.hasData) {
              final books = snapshot.data!;
              return ListView.builder(
                itemCount: books.length,
                itemBuilder: (context, index) {
                  final book = books[index];
                  return ListTile(
                    title: Text(book['title']),
                    subtitle: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Author: ${book['author']}'),
                        Text('Price: ${book['price']}'),
                      ],
                    ),
                    trailing: ElevatedButton(
                      onPressed: () async {
                        final authProvider =
                            Provider.of<AuthProvider>(context, listen: false);
                        final accessToken = authProvider.accessToken;
                        final url =
                            'http://127.0.0.1:8000/api/books/${books[index]['id']}/return/';
                        final response = await http.put(
                          Uri.parse(url),
                          headers: <String, String>{
                            'Content-Type': 'application/json; charset=UTF-8',
                            'Authorization': 'Bearer $accessToken',
                          },
                        );
                        if (response.statusCode == 200) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text('Book returned successfully'),
                            ),
                          );
                          setState(() {
                            _booksFuture = _fetchBooks(accessToken);
                          });
                        } else {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text('Failed to return book'),
                            ),
                          );
                        }
                      },
                      child: Text('Return'),
                    ),
                  );
                },
              );
            } else {
              return Center(
                child: Text('No books rented'),
              );
            }
          } else {
            return Center(
              child: CircularProgressIndicator(),
            );
          }
        },
      ),
    );
  }
}
