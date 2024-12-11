from django.db import models


class UserTypeChoices(models.TextChoices):
    ADOPTER = "Adopter", "Adopter"
    SHELTER = "Shelter", "Shelter"


class BulgarianProvinces(models.TextChoices):
    BLAGOEVGRAD = "Blagoevgrad", "Blagoevgrad"
    BURGAS = "Burgas", "Burgas"
    DOBRICH = "Dobrich", "Dobrich"
    GABROVO = "Gabrovo", "Gabrovo"
    HASKOVO = "Haskovo", "Haskovo"
    KARDZHALI = "Kardzhali", "Kardzhali"
    KYUSTENDIL = "Kyustendil", "Kyustendil"
    LOVECH = "Lovech", "Lovech"
    MONTANA = "Montana", "Montana"
    PAZARDZHIK = "Pazardzhik", "Pazardzhik"
    PERNIK = "Pernik", "Pernik"
    PLEVEN = "Pleven", "Pleven"
    PLOVDIV = "Plovdiv", "Plovdiv"
    RAZGRAD = "Razgrad", "Razgrad"
    RUSE = "Ruse", "Ruse"
    SHUMEN = "Shumen", "Shumen"
    SILISTRA = "Silistra", "Silistra"
    SLIVEN = "Sliven", "Sliven"
    SMOLYAN = "Smolyan", "Smolyan"
    SOFIA_CITY = "Sofia City", "Sofia City"
    SOFIA_PROVINCE = "Sofia Province", "Sofia Province"
    STARA_ZAGORA = "Stara Zagora", "Stara Zagora"
    TARGOVISHTE = "Targovishte", "Targovishte"
    VARNA = "Varna", "Varna"
    VELIKO_TARNOVO = "Veliko Tarnovo", "Veliko Tarnovo"
    VIDIN = "Vidin", "Vidin"
    VRATSA = "Vratsa", "Vratsa"
    YAMBOL = "Yambol", "Yambol"
