gcc -std=c99 -no-pie kovogame.c -o app
sed 's/dctf{wow_you_are_smart}/dctf{_not_a_real_flag_}/g' app >player_app
chmod +x ./player_app
