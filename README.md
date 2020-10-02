# Changing_proxy

Changing_Proxy (HTTP-TOR Proxy) based on Squid and torghost (https://github.com/SusmithKrishnan/torghost)

Proxy changes IP-address every 10 seconds

## Installation

- git clone https://github.com/Parkhomets/changing_proxy
- cd changing_proxy
- docker build -t changing_proxy .


## Usage

- docker run --cap-add=NET_ADMIN --name tor1 -t -p 5000:5000 changing_proxy
- сonfigure your browser | proxychains | python requests and so on via localhost:5000