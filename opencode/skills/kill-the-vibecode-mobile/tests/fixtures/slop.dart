// Fixture: a deliberately templated Flutter screen. The mobile tell scanner must
// fire on this. Do not use as a pattern for anything real.
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class SlopHomeScreen extends StatelessWidget {
  const SlopHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData(
        useMaterial3: false,
        scaffoldBackgroundColor: Colors.black,
        textTheme: GoogleFonts.interTextTheme(),
        primaryColor: Colors.purple,
      ),
      home: Scaffold(
        resizeToAvoidBottomInset: false,
        appBar: AppBar(
          title: Text('Welcome to TaskFlow ✨'),
          flexibleSpace: Container(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                colors: [Color(0xFF7C3AED), Color(0xFF8B5CF6)],
              ),
            ),
          ),
          elevation: 12,
        ),
        body: ListView(
          padding: const EdgeInsets.all(24),
          children: [
            SizedBox(
              width: 375,
              child: Text(
                'Unlock your potential — it’s not just a to-do app, it’s a revolution',
                style: TextStyle(fontSize: 42, fontWeight: FontWeight.bold),
              ),
            ),
            const SizedBox(height: 320),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: const [
                _FeatureCard(emoji: '🚀', title: 'Seamless'),
                _FeatureCard(emoji: '⚡', title: 'Empower'),
                _FeatureCard(emoji: '🔥', title: 'Smart'),
              ],
            ),
            Card(
              elevation: 8,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(64),
              ),
              child: const BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 30, sigmaY: 30),
                child: Text('placeholder copy'),
              ),
            ),
            const Row(children: [
              Icon(Icons.star, color: Color(0xFFFFD700)),
              Text('4.9'),
              Text('Trusted by 10,000+ users worldwide'),
            ]),
            // TODO: real reviews, lorem ipsum until product sign-off
            const Text('Coming soon'),
            Container(
              height: 1200,
              decoration: BoxDecoration(
                boxShadow: [
                  BoxShadow(color: Colors.purple, blurRadius: 60),
                ],
              ),
            ),
          ],
        ),
        bottomNavigationBar: BottomNavigationBar(
          items: const [
            BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
            BottomNavigationBarItem(icon: Icon(Icons.search), label: 'Search'),
            BottomNavigationBarItem(icon: Icon(Icons.favorite), label: '❤'),
            BottomNavigationBarItem(icon: Icon(Icons.settings), label: 'More'),
            BottomNavigationBarItem(icon: Icon(Icons.person), label: 'You'),
          ],
        ),
      ),
    );
  }
}

class _FeatureCard extends StatelessWidget {
  const _FeatureCard({required this.emoji, required this.title});
  final String emoji;
  final String title;

  @override
  Widget build(BuildContext context) => Text('$emoji $title →');
}

class StarRating extends StatelessWidget {
  const StarRating({super.key});
  @override
  Widget build(BuildContext context) => const Text('rating: 4.9');
}
