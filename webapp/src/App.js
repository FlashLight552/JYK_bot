import React, { useState, useEffect } from "react";

import "./App.css";
import geo from "./assets/geo.gif";
import checkmark from "./assets/checkmark2.gif";
import crossmark from "./assets/cross_mark.gif";
import logo_white from "./assets/logo-white.svg";

function App() {
  const tg = window.Telegram.WebApp;

  tg.ready();
  tg.expand();

  tg.onEvent("mainButtonClicked", function () {
    let lat = document.getElementById("lat").innerHTML;
    let lon = document.getElementById("lon").innerHTML;
    tg.sendData(lat + ":" + lon);
  });

  const getLocation = () => {
    let geolocation = navigator.geolocation;
    geolocation.getCurrentPosition(success, error);
  };

  let success = (position) => {
    let latitude = position.coords.latitude;
    let longitude = position.coords.longitude;
    setLocation({ lat: latitude, lon: longitude });

    tg.MainButton.text = "Отправить геолокацию";
    tg.MainButton.show();
    setTypeText(successText);
    setTypeGif(checkmark);
  };

  let error = () => {
    setTypeGif(crossmark);
    setTypeText(errorText);
  };

  const welcomeText = 'Тут должна быть какая-то сверх важная информация...'
  const successText = 'Геолокация успешно определена, нажмите кнопку отправить'
  const errorText = 'Геолокация не была определена, возможно, Вы не разрешили этого'

  const [location, setLocation] = useState({ lat: 0, lon: 0 });
  const [typeGif, setTypeGif] = useState(geo);
  const [typeText, setTypeText] = useState(welcomeText);

  useEffect(() => {
    getLocation();
  });

  return (
    <div className="App">
      <header className="header">
        <img src={logo_white} alt="logo" className="logo"></img>
        <span>Jewish Youth Kyiv bot</span>
      </header>

      <div className="content">
        <div className="content-text">
          <span>{typeText}</span>
        </div>
        <div className="content-gif">
          <img src={typeGif} alt="loading..." className="gif" />
          <span className="lat" id="lat" style={{ display: "none" }}>
            {location.lat}
          </span>
          <span className="lon" id="lon" style={{ display: "none" }}>
            {location.lon}
          </span>
        </div>
      </div>
    </div>
  );
}

export default App;
