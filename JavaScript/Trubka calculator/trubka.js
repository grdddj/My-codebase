function spocitej_vysledky() {
  const delka_polotovaru = parseInt($("#delka_polotovaru").val());
  const delka_odpadu = parseInt($("#delka_odpadu").val());
  const delka_odrezu = parseInt($("#delka_odrezu").val());

  let delky_vsech_trubek = [];

  $('.pocet_a_velikost').each(function(i, moznost) {
    const delka_trubky =  parseInt($(`#${moznost.id}_delka`).val());
    const pocet_trubek =  parseInt($(`#${moznost.id}_pocet`).val());
    for (let i = 0; i < pocet_trubek; i++) {
      delky_vsech_trubek.push(delka_trubky);
    }

  });

  let trubky_od_nejdelsi_po_nejkratsi = delky_vsech_trubek.sort(function(a,b) {return b - a;});


  let vysledne_trubky_s_jejich_detaily = [];
  vysledne_trubky_s_jejich_detaily.push(
    {
      cislo: 1,
      delka: 0,
      odpad: delka_polotovaru,
      rezy: []
    }
  )

  while (trubky_od_nejdelsi_po_nejkratsi.length > 0) {
    let pridali_jsme_novou_trubku = false;
    const trubka_se_kterou_pracujeme = vysledne_trubky_s_jejich_detaily[vysledne_trubky_s_jejich_detaily.length - 1]
    const momentalni_delka_pridavane_trubky = trubka_se_kterou_pracujeme.delka
    for (let i = 0; i < trubky_od_nejdelsi_po_nejkratsi.length; i++) {
      const delka_potencialni_nove_trubky = trubky_od_nejdelsi_po_nejkratsi[i];
      const potencialni_delka_nove_trubky_s_odrezem = delka_potencialni_nove_trubky + delka_odrezu
      const potencialni_nova_delka_pridavane_trubky = momentalni_delka_pridavane_trubky + potencialni_delka_nove_trubky_s_odrezem
      if (potencialni_nova_delka_pridavane_trubky <= delka_polotovaru) {
        pridali_jsme_novou_trubku = true;
        trubka_se_kterou_pracujeme.delka = potencialni_nova_delka_pridavane_trubky;
        trubka_se_kterou_pracujeme.odpad = delka_polotovaru - potencialni_nova_delka_pridavane_trubky;
        trubka_se_kterou_pracujeme.rezy.push(delka_potencialni_nove_trubky);
        trubky_od_nejdelsi_po_nejkratsi.splice(i, 1);
        break;
      }
    }

    if (pridali_jsme_novou_trubku === false) {
      poradove_cislo_nove_trubky = vysledne_trubky_s_jejich_detaily.length + 1;
      nova_trubka = {
        cislo: poradove_cislo_nove_trubky,
        delka: 0,
        odpad: delka_polotovaru,
        rezy: []
      };
      vysledne_trubky_s_jejich_detaily.push(nova_trubka);
    }
  }

  let celkovy_odpad = 0;
  for (let i = 0; i < vysledne_trubky_s_jejich_detaily.length; i++) {
    celkovy_odpad += vysledne_trubky_s_jejich_detaily[i].odpad;
  }

  const vysledek = {
    pocet_trubek: vysledne_trubky_s_jejich_detaily.length,
    celkovy_odpad: celkovy_odpad,
    trubky_detaily: vysledne_trubky_s_jejich_detaily
  }

  return vysledek;
}

function pridej_novou_moznost() {
  const pocet_moznych_trubek = $(".pocet_a_velikost").length
  const novy_index = pocet_moznych_trubek + 1
  $("#pocty_a_velikosti").append(
    `
    <p id="trubka_${novy_index}" class="pocet_a_velikost">
      Délka trubky [mm]
      <input id="trubka_${novy_index}_delka" type="number" name="" value="${novy_index}" placeholder="Délka trubky">

      Počet trubek
      <input id="trubka_${novy_index}_pocet" type="number" name="" value="${novy_index}" placeholder="Počet trubek">

      <button class="vymaz_trubku btn btn-primary red" name="trubka_${novy_index}">Vymaž trubku!</button>
    </p>
    `
  );
  $(".vymaz_trubku").click(function(){
    vymaz_trubku(event);
  });
}

function vymaz_trubku(event) {
  const moznost_na_vymaz = event.target.name;
  $("#" + moznost_na_vymaz).remove();
}

function zobraz_vysledky_do_tabulky(trubky_detaily) {
  for (let i = 0; i < trubky_detaily.length; i++) {
    $("#detaily_trubek").append(
      `
      <tr>
        <td> ${trubky_detaily[i].cislo} </td>
        <td> ${trubky_detaily[i].odpad} (+${$("#delka_odpadu").val()}) </td>
        <td> ${trubky_detaily[i].rezy} </td>
      </tr>"
      `
    );
  }
}

function pocitej() {
  odstran_predchozi_vysledky();
  vysledky = spocitej_vysledky();
  $("#pocet_trubek").html(vysledky.pocet_trubek);
  $("#celkovy_odpad").html(
      `${vysledky.celkovy_odpad} (+${vysledky.pocet_trubek}*${$("#delka_odpadu").val()})`
  );
  zobraz_vysledky_do_tabulky(vysledky.trubky_detaily);
}

function odstran_predchozi_vysledky() {
  $("#detaily_trubek").html(
    `
      <tr>
        <th>Číslo trubky</th>
        <th>Zbytek [mm]</th>
        <th>Jednotlivé řezy [mm]</th>
      </tr>
    `
  );
  $("#pocet_trubek").html("");
  $("#celkovy_odpad").html("");
}

$(document).ready(function(){
  $("#pocitej").click(function(){
    pocitej();
    console.log("Spočítáno!");
  });
  $("#pridej_trubku").click(function(){
    pridej_novou_moznost();
    console.log("Trubka přidána!");
  });
  $(".vymaz_trubku").click(function(){
    vymaz_trubku(event);
    console.log("Trubka vymazána!");
  });
});
