import logoUniversita from "../assets/pratiche-universita.png";
import logoEduNews24 from "../assets/edunews24/logo.svg";

// Originale estratto da https://uni.ersaf.it/images/PraticheUniversita.png.
export const LOGO_UNIVERSITA = {
  src: logoUniversita,
  alt: "Pratiche Università — Contrattualistica Percorsi Accademici",
  width: 1670,
  height: 580,
};

// Tracciati del logo nell'intestazione del sito di EduNews24 (news1,
// src/components/Header.astro), senza le classi dell'animazione d'ingresso.
// Solo nella testata del modulo in Dashboard e della pagina, mai nel menu.
export const LOGO_EDUNEWS24 = {
  src: logoEduNews24,
  alt: "EduNews24",
  width: 209,
  height: 41,
};
