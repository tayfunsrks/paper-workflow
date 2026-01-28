kitaplar için özelleştirilmiş #kitapmaria

written by theban & zorgof

Eksikler:

Şöyle ikili yapmaya çalıştım olmadı. Kitap Adı uzun olunca üç nokta atıyor. Orada ikiye bölen bir fonksiyon yazdım. \n karakteri ikiye bölüyor dediler pyrogram çetinde ama işe yaramadı. Ya da ben yapamadım.

Dosya adı uzunluğu max 60 karakter

Multimongo hesabını bağlama (belki)

Ayrıca:

OSMANLI BELGELERİNDE ERMENİ İSYANLARI(1895-1896)-2.pdf

İsimli dosya

Osmanlı şeklinde çıkmıyor.

OsmanlI şeklinde çıkıyor.

Muhtemelen vt kaynaklı case sorunu 

---
O anda indexlenen çet bilgilerini göster ✅ 

Banlananlara mesaj gönderME✅ 

/yay broadcast komutu.

- Herkes: ne ver ne yok herkese
- Üyeler: kanal üyeleri

✅ Sadece inline seçeneği

✅ Sadece butonlar seçeneği

✅ Tek hoş geldin mesajı seçeneği

✅ Bildirim açma kapama: /ayarlar

✅ Buton sayıları düzeltildi. İstediğiniz sayıyı verin. 10 öntanımlı.

✅ Link oluşturma hatası düzeltildi:

- linki 1 kişi için oluşturur eğer kanal gizliyse. "member limit invalid" hatası verirse member limiti olmadan oluşturur.

Komutlar:

- /invite (chat id) link oluşturur
- /izinler (chat id) çet bilgisi ve botun o çetteki izinleri
- /ayarlar ayarlar sayfası
- /virustotal dosya tarayıcı
- /wayback web sayfasını arşivler
- /ping pingler
- /json mesajı jsonlar
- /hash dosya md5, sha1, sha256 hesaplar
- /sil dosya siler
- /deleteallusers vtdan kullanıcıları siler
- /deleteallgroups vtdan grupları siler
- /deleteallfiles vtdan dosyaları siler

2.0.7:

- database / iafilterdb : dosyaları vt'a yazarken gereksizleri yazmamayı sağlar. save_file fonksiyonu.
- Member limit problemi kökten çözüldü
- Artık kanala katılın mesajı, üye kanala katılınca silinecek.
- Virustotal iyileştirmeleri
- Türkçeleştirmeler, gereksiz şeyler silindi, çeşitli refactoringler
- Kanaldan çıkanları otomatik banlama,
- Seçenekli banlandın mesajı,
- Logging özelleştirmeleri

2.0.8:

- İndexleme iptal ya da sonunda fromid sıfırlanır
- kişiye özel buton sayıları:
    - BUTTON_COUNT_ENHANCER i 0 yaparsanız tüm üyeler için DEF_BUTTON_COUNT geçerli olur.
- CUSTOM_FILE_CAPTION artık CUSTOM_CAPTION oldu. ona göre configinizi güncelleyin.
-/json eklendi - mesaja yanıtlayın
-/ayarlar kaldırıldı - gereksiz, ayarlara girin zaten var.
-translation.py silindi - gereksiz
-start.sh silindi - gereksiz: pip3 install -r requirements.txt && python3 bot.py
-admin helpleri tekleştirildi. - ayarlardaki yardım sadece adminlere görünür.
-artık hiçbir yerde none yazmayacak.
-DISABLE_FILE_SAVE - otomatik dosya kaydetmesi artık seçenekli

2.0.9:

- kritik hatalar düzeltildi
- butonlara info ve kapatma düğmeleri
- çeşitli refactoringler
- yeniayrılmada yasakla butonu çıkmıyordu fixlendi
- doğdum / öldüm bot sürümü eklendi
- logging.conf silindi, logger basitleştirildi, sorunları çözüldü.
- klon dosyaların sonu geldi:

- vt'a kaydederken:
    - aynı dosya adı varsa:
        - Ve aynı boyuttaysa:
            - dosya captionu daha uzun olanı kaydet

- çift dosyalar bu şekilde önlenmiş oldu.

2.0.9.1 hotfix :D

- indexleme sorunu çözüldü
- artık kanala katılmadıysa mesajını silecek. yani botu bulamayacak
- kopya dosyalarda dosya tipi de dikkate alınacak
    - örneğin aynı dosya video ve doküman olarak varsa ikisi de kaydedilir
- banlı kullanıcılar hiçbir şey yapamaz
- butonlar düzeltildi
- çeşitli refactoringler
- logger adam edildi, hem dosya hem terminal tertemiz
- logger saati türkiyeye ayarlandı
- bu güncelleme yeniden index gerektirir !

2.0.10 beta:

- türçe arama sorunu çözüldü.
- inline yardımmesajları
- caption hataları çözüldü
- daha fazla kapatma düğmesi
- index bitince bitti diyecek
- ayarlar tuşu sadece ilgili kullanıcıya çalışacak
- banlı çet ve kullanıcılar artık düzgün çalışmalı
- /ban /unban artık auth channelden de banlar
- bu güncelleme yeniden index gerektirir !

2.0.11 alfa:

- indexleme eskiye döndürüldü. başka zaman başka çözüm bulunacak
- parantezler tekrar eklendi sorun çıkarıyordu.
- banlı kullanıcılara link oluşturMA
- hata düzeltmeleri refactoringler vb.
- bu güncelleme yeniden index gerektirir !

2.0.12 alfa:

- ufak tefek görsel hatalar
- vt kaydederken { } [ ] ( ) gibi karakterler yerine boşluk kullanılacak
- Osmanlı - OSMANLI - osmanlI aynı sonuçları verecek
- indexlemede doğru görünmeyen şeyler düzeltildi

2.0.13 alfa:
- dosya caption sınırları eklendi. (4096)
    - eğer dosyanızın captionu bu sınırdaysa custom caption gönderilmez.
- /index fonksiyonu eklendi. tüm dosyaları bulmaya yarar
    - INDEXER_MAX = 1000 maximum sonuç bulur. iyi ellemeyin.
    - DISABLE_INDEXER info.py den okuyun
- NO_SAVE_SUFFIX dinamik hale getirildi
- NO_SAVE_FULLNAME dinamik hale getirildi
- indexleme mesajı pinlenecek
- yeniden loglama kolaylaştırıldı
- loglamaya tarih eklendi
- /log 45 son 45 satırı gönderir
- daha fazla temizleyici eklendi
- giden dosyalar eklendi. bugün gönderilen dosyaların boyutu anlamında. inline ı saymaz malesef.
- ıvır zıvır yerlere thumbnailler eklendi.
    - LINK_FOR_ABOUT_PIC değişkeninizi LOGO_LINK olarak değiştirin. bu tüm thumbnailleriniz olacak.
- 2.0.12 den geliyorsanız yeniden index gerektirmez

2.0.14 alfa:
- FILENAME_SPLITTER eklendi. info.pyden okuyun
- işlenen ve işlenecek mssajlar gösterimi
- daha hızlı güncelle
- config.env alımı düzeltildi. lokalde varsa onu kullanır yoksa config.env içinde yazılı olan url ile çeker.
- index bitimi veya iptalinde skip number görünecek
- dosya sonu custom Captionla bitiyorsa onu silerek gönder. 2 kez yazılmasını engeller.
- bot Uptime & os Uptime
- hız düzeltildi > alınan toplam messages total olmalıydı.
- string hataları yazım yanlışları düzeltildi

2.0.15 alfa:
- artık kanaldan dosya düzenlerseniz düzenlenmiş hali ile kaydolur.
- log iyileştirildi
- login desteği eklendi. isteğe bağlı.
    - LOGIN_MODE true / false
    - LOGIN_PASSWORD
    - LOGIN_WARNING giriş yapın uyarısı
    - /giris ve /login komutlarına bağlı
- artık broadcast mesajları sessiz olacak.
- artık wayback komutu /wayback ve /wb olarak çalışıyor
- artık banlanan kullanıcılar vtdan silinecek.
- artık kesinlikle: (kanalda banlı, kanalda yok, vt'da banlı) kişiye broadcast yapılmaz
- tüm floodwaitler iyileştirildi
- inline kapalı modu iyileştirildi. artık yuvarlak dönüp durmayacak

2.0.15.1 hotfix alfa:
- filters düzeltildi
    - `/baglan` `/bağlan` `/connect` yazarak gruba bağlanabilirsiniz
    - `/ayrıl `/ayril` `/disconnect` yazarak grup bağını kesebilirsiniz
    - `/baglar` `/ bağlar` `/connections` bağlı grupları görebilirsiniz
- parsemode hataları fixlendi
- /id komutu eklendi
- heroku şeyleri eklendi:
    - `/restart dyno` - dynoyu restart eder
    - `/restart kill` - dynoyu öldürür
    - `/restart` - sikindirik restart
    - `HEROKU_API_KEY` ve `HEROKU_APP_NAME` i herokuya ekleyin. gist'teki configinize eklemeyin.
- çoklu parola desteği. virgül ile ayırın.
    - örnek: `pasaport,şifre,ikincişifre,boşluklu örnek şifre`
    - boşluklu parola da girilebilir. örnek: `boşluklu örnek şifre,ikincibosluksuzsifre`
- türkçeleştirmeler
- inline & login düzeltildi
- sourcery ai refactored

2.0.15.2 alfa:
- bilinen hatalar fixlendi
- login ve subscribe fonksiyona alındı
- auth userlar için db ya da issubscribed işlemleri es geçilir. çünkü adam auth user amk
- veritabanına yapılan tüm gereksiz istekler onarıldı. bot daha stabil çalışacak.
- dosya caption sınırları düzeltildi (1024)

2.0.15.3 alfa:
- virustotal düzeltildi
- github denen *** a karşı gitlab snippets urlsi ile config alma eklendi:
    - bu daha güvenli bir yöntem. kullanmanızı öneririm
    - oluşturun: https://gitlab.com/dashboard/snippets
    - diyelim ki oluşturduğunuz config textinin urlsi bu: https://gitlab.com/-/snippets/2523453
    - bu durumda id 2523453 olacak
    - apikeyi şu şekilde alıyoruz:
        - https://gitlab.com/-/profile/personal_access_tokens e gir
        - en üstteki api yi seç yeterli, token adı ver, onlarca yıl sonrasını seç ve kopyala
        - diyelim ki tokenimiz şu: dgsdfg1541-s6d5g1sd6g-sd1fg6sd1g-sdfg51
    - `CONFIG_FILE_URL` a bir boşluk bırakarak giriyoruz, sıra önemli:
        - 2523453 dgsdfg1541-s6d5g1sd6g-sd1fg6sd1g-sdfg51
    - nasıl yaptığımı merak ediyorsanız buyrun:
        - https://docs.gitlab.com/ee/api/snippets.html
        - get_config_from_url() fonksiyonuna da bakınız

2.0.15.4 alfa:
- gitlab ci deploy eklendi - canım çıktı aq

2.1.0.0 beta:
- master slave' e merhaba deyin:
    - köle botlar sayesinde herkes kendi botunu oluşturabilir
    - inline çalışmıyor. üzerinde çalışacak olan varsa buyursun
    - /kole (bot api) - köle ekler
    - /koleler - tüm köleleri gösterir
    - /kolesil (bot api ya da @botusername) - köleyi siler
    - köleler vta eklenir. bot başlangıcında çekilir, silinmiş olanlar vtdan temizlenir.
    - yeni köle eklediğinizde botu yeniden başlatmalısınız. anında çalıştırmak güvenli değildi sildim kodları
    - `TEMP_CHANNEL` değişkenini doldurun, yeni eklediğiniz köleleri elle kanala eklemelisiniz. ana bot da bu kanalda olmalı.
    - SAKIN köle botları depo kanalınıza eklemeyin! yapmanız gereken tek şey yukarıdaki.
    - yapınca temp kanalına bir mesaj gönderin nokta gibi ya da at daşşağı fotosu da olur.
    - bunu yaparak bota diyoruz ki bak böyle bir kanal var ve orada yöneticisin haberin olsun. yoksa sıkıntı çıkarabilir.
    - köle botların tümünde adminsiniz. veritabanında banladığınız user'lar hiçbir klonu da kullanamaz.
    - köle botların sadece temp kanalına yönetici olarak eklenmesi gerekiyor. ana depoya eklemeyin.
    - auth channel köle botlar için devredışıdır. niye diye sormazsınız herhalde :D

2.1.0.1 alfa:
- sonsuz sayıda (teorik olarak) bot bağlanabilir
- `TEMP_CHANNEL` değişkeniniz public bir kanal olsun.
- köle botları temp channel a da eklemeyin. gerek yok.
- birden çok kanal olmasın diyorsanız `TEMP_CHANNEL` ve `LOG_CHANNEL` aynı kanal olabilir. tavsiye etmem. tavsiyem:
    - `LOG_CHANNEL` kendi kişisel id'niz olsun
    - `TEMP_CHANNEL` public, sadece ana bot ve siz varsınız. bu değişkeniniz şu şekilde olmalı: `@korpiracy`
    - hayırlı cumalar