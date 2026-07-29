# 12 — Firebase Standards (legacy en salida)

> Estado declarado en el stack canónico: **Firebase está en salida**. Estas reglas gobiernan la
> transición, no el crecimiento.

- **[REQUIRED]** Prohibido usar Firebase en proyectos NUEVOS (auth, Firestore, hosting, functions).
  El equivalente Supabase/Cloudflare ya existe para cada caso: Auth→Supabase Auth,
  Firestore→Postgres/KV, Hosting→Pages, Functions→Workers.
- **[REQUIRED]** Inventario vivo: los proyectos `*.web.app` en producción (tradingpropanel,
  ia-post, pwagastos, ingenius…) se listan en [28-Knowledge-Base.md](28-Knowledge-Base.md) con su
  estado de migración: `activo-firebase` · `migrando` · `migrado`.
- **[REQUIRED]** Mientras un proyecto siga en Firebase: sus reglas de Firestore/Storage se auditan
  igual (nada de `allow read, write: if true` en producción) y su `firebaseConfig` puede vivir en
  frontend (es público por diseño) pero las claves admin/service-account JAMÁS.
- **[RECOMMENDED]** Criterio de migración: se migra un proyecto Firebase cuando (a) hay que
  tocarlo por otra razón, o (b) genera costo, o (c) bloquea una feature. No se migra por limpieza
  — hay 60 proyectos y ~6 activos; el esfuerzo va a los activos.
- Restos de Firebase en repos ya migrados (ej. `firebase.json`/`.firebaserc` en jcdigital, que ya
  despliega en Pages): se eliminan al siguiente commit que toque el repo.
