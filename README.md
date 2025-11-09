# WiFiLess

WiFiLess is a versatile system that simplifies networking and information collection in a variety of settings, from career fairs to customer engagement events. By leveraging a Raspberry Pi 4 as a hotspot with a captive portal, WiFiLess enables users to submit data such as surveys, contact details, or feedback, even in environments with unreliable WiFi.

## Features
- Raspberry Pi 4 hotspot acting as an Access Point
- Captive portal interface for submitting surveys or job applications
- File upload support for resumes (PDF, DOCX, DOC, TXT)
- Admin panel to toggle between different modes (Survey / Job Application)
- Local database (SQLite) and CSV backup for storing submissions

---

## How It Works
1. The Raspberry Pi broadcasts a WiFi network that clients can connect to.
2. Once connected, users are redirected to a captive portal hosted on the Pi.
3. The portal serves either a survey page or a job application page depending on the selected mode.
4. Users can submit information, including uploading their resume, which is stored securely on the Pi.
5. Admins can control the portal via a web interface to switch between modes.

---

## Sources & How We Used Them

### 1. [ChatGPT](https://chat.openai.com/)
- Assisted in debugging, and improving Python and HTML code for the Flask server.
- Helped design and refine the user interface for both the survey and job application pages.
- Provided guidance on integrating file uploads, SQLite database handling, and admin panel functionality.

### 2. [Flask](https://flask.palletsprojects.com/)
- Served as the main Python web framework for hosting the captive portal and survey/job application forms.
- Managed routing, form submission, and rendering of HTML templates.
- Enabled dynamic page serving and handling of file uploads.

### 3. [HostAPD](https://w1.fi/hostapd/)
- Used to configure the Raspberry Pi as a WiFi access point.
- Allowed the Pi to broadcast a hotspot that clients could connect to for accessing the captive portal.
- Provided the necessary backend for networking the captive portal environment.

---

### Requirements
- Raspberry Pi 3 / 4 / Zero 2 W (with built-in Wi-Fi)
- Raspberry Pi OS (Bookworm or Bullseye) or Ubuntu 22.04+
- Python 3.9+
- `hostapd`, `dnsmasq`, `iptables` or `nftables`
- Optional: Firefox (for kiosk mode)

### Installation

### 1 Clone This R-epository
> git clone https://github.com/<your-username>/piportal.git <br>
> cd PresenterDevice

### 2 Install Packages and Edit Configuration Files
> python3 -m venv .venv <br>
> source .venv/bin/activate <br>
> pip install -r requirements.txt <br>
> sudo apt install hostapd dnsmasq <br>
> sudo systemctl stop hostapd <br>
> sudo systemctl stop dnsmasq

Edit /etc/dhcpcd.conf:
>interface wlan0 <br>
>    static ip_address=192.168.4.1/24 <br>
>    nohook wpa_supplicant


Edit /etc/dnsmasq.conf:
>interface=wlan0 <br>
>dhcp-range=192.168.4.2,192.168.4.50,255.255.255.0,24h <br>
>address=/#/192.168.4.1


Edit Configure /etc/hostapd/hostapd.conf:
>interface=wlan0 <br>
>driver=nl80211 <br>
>ssid=PiPortal <br>
>hw_mode=g <br>
>channel=7 <br>
>auth_algs=1 <br>
>ignore_broadcast_ssid=0 <br>
> sudo systemctl unmask hostapd <br>
> sudo systemctl enable hostapd dnsmasq <br>
> sudo systemctl start hostapd dnsmasq

### 3 Run 
> Run with ./start.sh







