import React, { useState, useEffect } from "react";

import geo from "../assets/geo.gif";
import checkmark from "../assets/checkmark2.gif";
import crossmark from "../assets/cross_mark.gif";
import logo_white from "../assets/logo-white.svg";
import logo_black from "../assets/logo-black.svg";

function Geo() {
  const tg = window.Telegram.WebApp;

  const getLocation = () => {
    let geolocation = navigator.geolocation;
    geolocation.getCurrentPosition(success, error);
  };

  let success = (position) => {
    let latitude = position.coords.latitude;
    let longitude = position.coords.longitude;
    location.current = `${latitude}:${longitude}`;

    tg.MainButton.text = "Отправить геолокацию";
    tg.MainButton.show();
    tg.onEvent("mainButtonClicked", function () {
      tg.sendData(location.current);
    });

    setTypeText(successText);
    setTypeGif(checkmark);
  };

  let error = () => {
    tg.MainButton.text = "Закрить";
    tg.MainButton.show();
    tg.onEvent("mainButtonClicked", function () {
      tg.close();
    });

    setTypeGif(crossmark);
    setTypeText(errorText);
  };

  const welcomeText = "Тут должна быть какая-то сверх важная информация...";
  const successText = "Геолокация успешно определена, нажмите кнопку отправить";
  const errorText =
    "Геолокация не была определена, возможно, Вы не разрешили этого";

  const [typeGif, setTypeGif] = useState(geo);
  const [typeText, setTypeText] = useState(welcomeText);
  const [typeLogo, setTypeLogo] = useState(logo_white);
  const [isLoaded, setIsLoad] = useState(false);

  const location = React.useRef("0:0");

  useEffect(() => {
    setIsLoad(true);
  }, []);

  useEffect(() => {
    if (isLoaded) {
      getLocation();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isLoaded]);

  useEffect(() => {
    if (isLoaded) {
      tg.ready();
      tg.expand();
      let colorSheme = tg.colorScheme;

      if (colorSheme === "light") {
        setTypeLogo(logo_black);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isLoaded]);

  return (
    <div className="geo">
      <header className="header">
        <img src={typeLogo} alt="logo" className="logo"></img>
      </header>

      <div className="content">
        <div className="content-gif">
          <img src={typeGif} alt="loading..." className="gif" />
        </div>

        <div className="content-text">
          <span>{typeText}</span>
        </div>
      </div>
    </div>
  );
}

export default Geo;
