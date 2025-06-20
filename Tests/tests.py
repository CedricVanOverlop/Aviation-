from Classes import Meteo

def test_wind_status():
    meteo1 = Meteo(20, 45, "aucune")
    assert meteo1.wind_status() == "attention", "Doit être considéré comme vent fort (attention)"
    
    meteo2 = Meteo(20, 20, "aucune")
    assert meteo2.wind_status() == "ok", "Doit être considéré comme vent faible (ok)"
    
    meteo3 = Meteo(20, 65, "aucune")
    assert meteo3.wind_status() == "danger", "Doit être considéré comme vent très fort (danger)"

def test_is_rainy():
    meteo1 = Meteo(10, 10, "pluie")
    assert meteo1.is_rainy() == True, "Doit être considéré comme pluvieux"
    
    meteo2 = Meteo(10, 10, "soleil")
    assert meteo2.is_rainy() == False, "Doit être considéré comme non pluvieux"

if __name__ == "__main__":
    test_wind_status()
    test_is_rainy()
    print("Tous les tests Meteo sont passés !")
