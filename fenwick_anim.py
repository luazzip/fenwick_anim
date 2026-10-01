from manim import *

# ============================================================
#  CONTROL DE VELOCIDAD
#  1.0 = ritmo pensado para ~2 min en total (las 4 escenas)
#  Sube (1.3) para ir más lento, baja (0.9) para ir más rápido.
# ============================================================
SLOW = 1.0


# ============================================================
#  1) IMPLEMENTACIÓN REAL DEL FENWICK TREE (hecha a mano)
#     Las animaciones salen de los pasos que calcula esta clase.
# ============================================================
class Fenwick:
    def __init__(self, n):
        self.n = n
        self.t = [0] * (n + 1)          # el índice 0 NO se usa

    def update(self, i, delta):
        """Suma delta en la posición i. Devuelve las celdas tocadas."""
        steps = []
        while i <= self.n:
            self.t[i] += delta
            steps.append((i, self.t[i]))   # (celda, nuevo valor)
            i += i & -i                    # i + lowbit(i)
        return steps

    def query(self, i):
        """Suma de A[1..i]. Devuelve (total, pasos)."""
        total = 0
        steps = []
        while i > 0:
            total += self.t[i]
            steps.append((i, self.t[i], total))  # (celda, valor, acumulado)
            i -= i & -i                          # i - lowbit(i)
        return total, steps

    def range_query(self, l, r):
        return self.query(r)[0] - self.query(l - 1)[0]


# ============================================================
#  2) CONFIGURACIÓN VISUAL
# ============================================================
ARR = [3, 2, 5, 1, 4, 6, 2, 7]            # arreglo de ejemplo (n = 8)
W, H = 1.2, 0.9                           # ancho y alto de cada celda
ARR_Y, BIT_Y = 1.8, -0.9                  # altura de la fila A y de la fila tree
INFO_Y, RULE_Y, ACC_Y = -2.75, -3.2, -3.65
PALETTE = [YELLOW, TEAL, PINK, PURPLE]


class FenwickScene(Scene):
    """Clase base: dibuja el arreglo y el árbol, y tiene las animaciones
    reutilizables (update y query). Todas las escenas heredan de aquí."""

    # ---------- control de velocidad (multiplica todo por SLOW) ----------
    def play(self, *args, run_time=None, **kwargs):
        rt = 1.0 if run_time is None else run_time
        super().play(*args, run_time=rt * SLOW, **kwargs)

    def wait(self, duration=1.0, **kwargs):
        super().wait(duration * SLOW, **kwargs)

    # ---------- preparación ----------
    def x_of(self, i):
        return (i - (self.n + 1) / 2) * W

    def setup_fenwick(self, arr=ARR):
        self.n = len(arr)
        self.a = [0] + list(arr)
        self.fw = Fenwick(self.n)
        for i in range(1, self.n + 1):          # construcción REAL
            self.fw.update(i, arr[i - 1])

        self.info = self.rule = self.acc = self.title = None
        self.arr_box, self.arr_txt, self.arr_idx = {}, {}, {}
        self.bit_box, self.bit_txt, self.bit_idx, self.bit_bin = {}, {}, {}, {}

        for i in range(1, self.n + 1):
            x = self.x_of(i)
            # fila del arreglo original
            b = Rectangle(width=W - 0.1, height=H, color=WHITE,
                          fill_color=GREY_E, fill_opacity=1).move_to([x, ARR_Y, 0])
            self.arr_box[i] = b
            self.arr_txt[i] = Text(str(arr[i - 1]), font_size=30).move_to(b)
            self.arr_txt[i].set_z_index(10)     # SIEMPRE encima de las celdas
            self.arr_idx[i] = Text(str(i), font_size=22, color=GREY_B).next_to(b, UP, buff=0.22)
            # fila del Fenwick tree
            c = Rectangle(width=W - 0.1, height=H, color=BLUE,
                          fill_color=BLUE_E, fill_opacity=0.6).move_to([x, BIT_Y, 0])
            self.bit_box[i] = c
            self.bit_txt[i] = Text(str(self.fw.t[i]), font_size=30).move_to(c)
            self.bit_txt[i].set_z_index(10)     # SIEMPRE encima de las celdas
            self.bit_idx[i] = Text(str(i), font_size=22, color=GREY_B).next_to(c, DOWN, buff=0.1)
            self.bit_bin[i] = Text(format(i, "04b"), font_size=20, color=GREY_B,
                                   font="Monospace").next_to(self.bit_idx[i], DOWN, buff=0.05)

        self.lbl_a = Text("A", font_size=30, color=GREY_B).move_to([-5.9, ARR_Y, 0])
        self.lbl_bit = Text("tree", font_size=30, color=BLUE_B).move_to([-5.9, BIT_Y, 0])

    # ---------- utilidades de texto ----------
    def rng(self, l, r):
        return f"A[{r}]" if l == r else f"A[{l}..{r}]"

    def expr(self, l, r):
        """Devuelve '5 + 1 + 4' con los valores ACTUALES de A[l..r]."""
        return " + ".join(str(self.a[k]) for k in range(l, r + 1))

    # ---------- mostrar cosas ----------
    def show_array(self, run_time=1.5):
        anims = [AnimationGroup(FadeIn(self.arr_box[i], shift=DOWN * 0.3),
                                FadeIn(self.arr_txt[i], shift=DOWN * 0.3),
                                FadeIn(self.arr_idx[i], shift=DOWN * 0.3))
                 for i in range(1, self.n + 1)]
        self.play(FadeIn(self.lbl_a), LaggedStart(*anims, lag_ratio=0.12), run_time=run_time)

    def show_bit(self, filled=True, run_time=1.5):
        anims = []
        for i in range(1, self.n + 1):
            box = self.bit_box[i]
            if not filled:
                box.set_fill(opacity=0)           # celdas vacías (para la intro)
            parts = [FadeIn(box, shift=UP * 0.3), FadeIn(self.bit_idx[i]), FadeIn(self.bit_bin[i])]
            if filled:
                parts.append(FadeIn(self.bit_txt[i], shift=UP * 0.3))
            anims.append(AnimationGroup(*parts))
        self.play(FadeIn(self.lbl_bit), LaggedStart(*anims, lag_ratio=0.12), run_time=run_time)

    def set_title(self, msg):
        new = Text(msg, font_size=34).move_to([0, 3.45, 0])
        if self.title is None:
            self.play(Write(new), run_time=1.0)
        else:
            self.play(ReplacementTransform(self.title, new), run_time=1.0)
        self.title = new

    # ---------- textos de abajo (explicación, regla, acumulado) ----------
    def _mk(self, msg, y, size, color):
        t = Text(msg, font_size=size, color=color).move_to([0, y, 0])
        if t.width > 12.5:
            t.scale_to_fit_width(12.5)
        return t

    def _swap(self, old, new):
        return FadeIn(new) if old is None else ReplacementTransform(old, new)

    def say(self, msg, rule=None, acc=None, color=WHITE, hold=2.0, run_time=0.5, extra=None):
        """Cambia los textos de abajo y se queda 'hold' segundos para que se lea.
        'extra' son animaciones que ocurren al mismo tiempo."""
        anims = list(extra) if extra else []
        new = self._mk(msg, INFO_Y, 30, color)
        anims.append(self._swap(self.info, new)); self.info = new
        if rule is not None:
            r = self._mk(rule, RULE_Y, 26, YELLOW_B)
            anims.append(self._swap(self.rule, r)); self.rule = r
        if acc is not None:
            a = self._mk(acc, ACC_Y, 32, GREEN)
            anims.append(self._swap(self.acc, a)); self.acc = a
        self.play(*anims, run_time=run_time)
        if hold > 0:
            self.wait(hold)

    # ---------- figuras de ayuda ----------
    def span_rect(self, l, r, color):
        """Rectángulo translúcido sobre las celdas A[l..r]."""
        xc = (self.x_of(l) + self.x_of(r)) / 2
        rect = Rectangle(width=(r - l + 1) * W - 0.02, height=H + 0.3, color=color,
                         fill_color=color, fill_opacity=0.25,
                         stroke_width=5).move_to([xc, ARR_Y, 0])
        rect.set_z_index(3)
        return rect

    def cover(self, i, color):
        """Lo que cubre tree[i]: las últimas lowbit(i) celdas hasta i."""
        l = i - (i & -i) + 1
        return self.span_rect(l, i, color)

    def connector(self, i, rect, color):
        line = DashedLine(rect.get_bottom(), self.bit_box[i].get_top(),
                          color=color, stroke_width=4)
        line.set_z_index(2)
        return line

    def jump_arrow(self, a, b, color):
        arrow = CurvedArrow(self.bit_box[a].get_top() + UP * 0.05,
                            self.bit_box[b].get_top() + UP * 0.05,
                            angle=-TAU / 5, color=color)
        arrow.set_z_index(4)
        return arrow

    # ---------- OPERACIÓN: update ----------
    def animate_update(self, i, delta, color=ORANGE):
        steps = self.fw.update(i, delta)            # <- lógica real
        old = self.a[i]
        self.a[i] += delta
        sign = f"+{delta}" if delta >= 0 else str(delta)
        self.say(f"update({i}, {sign}): A[{i}] pasa de {old} a {self.a[i]}",
                 "regla: i = i + lowbit(i)   (mientras i <= n)", hold=1.8)

        new_a = Text(str(self.a[i]), font_size=30).move_to(self.arr_box[i])
        new_a.set_z_index(10)
        self.play(Transform(self.arr_txt[i], new_a),
                  self.arr_box[i].animate.set_stroke(GREEN, 6), run_time=0.9)
        self.arr_txt[i].set_z_index(10)
        self.wait(0.4)

        for k, (j, val) in enumerate(steps):
            lb = j & -j
            l = j - lb + 1
            nxt = j + lb
            end = nxt > self.n
            rect = self.cover(j, color)
            conn = self.connector(j, rect, color)
            # 1) mostramos qué elementos cubre tree[j]
            self.play(Create(rect), Create(conn),
                      self.bit_box[j].animate.set_stroke(color, 6), run_time=0.7)
            # 2) actualizamos el valor de la celda
            new_t = Text(str(val), font_size=30).move_to(self.bit_box[j])
            new_t.set_z_index(10)
            self.say(f"tree[{j}] cubre {self.rng(l, j)}: ahora vale {val}",
                     f"{j} ({j:04b}) + {lb} = {nxt}" +
                     ("   -> se sale del arreglo: FIN" if end else ""),
                     extra=[Transform(self.bit_txt[j], new_t),
                            self.bit_box[j].animate.set_fill(GREEN_E, 0.9)],
                     hold=1.3, run_time=0.7)
            self.bit_txt[j].set_z_index(10)
            # 3) saltamos a la siguiente celda
            extra = []
            if not end:
                arrow = self.jump_arrow(j, nxt, color)
                self.play(Create(arrow), run_time=0.5)
                extra.append(FadeOut(arrow))
                self.wait(0.2)
            self.play(FadeOut(rect), FadeOut(conn), *extra,
                      self.bit_box[j].animate.set_stroke(BLUE, 4), run_time=0.4)

        self.say(f"Solo se tocaron {len(steps)} de {self.n} celdas",
                 f"máximo posible: log2({self.n}) + 1 = {self.n.bit_length()} celdas",
                 hold=2.0)
        return steps

    # ---------- OPERACIÓN: query (suma de prefijo) ----------
    def animate_query(self, i, color=None, label="suma"):
        total, steps = self.fw.query(i)             # <- lógica real
        kept = VGroup()
        self.say(f"query({i}): empezamos en i = {i}",
                 "regla: i = i - lowbit(i)   (mientras i > 0)",
                 acc=f"{label} = 0", hold=1.2)

        for k, (j, val, run) in enumerate(steps):
            c = color if color is not None else PALETTE[k % len(PALETTE)]
            lb = j & -j
            l = j - lb + 1
            nxt = j - lb
            rect = self.cover(j, c)
            conn = self.connector(j, rect, c)
            self.play(Create(rect), Create(conn),
                      self.bit_box[j].animate.set_stroke(c, 6), run_time=0.7)
            fin = "   -> llegamos a 0: FIN" if nxt == 0 else ""
            self.say(f"tree[{j}] = {val}   ({self.rng(l, j)} = {self.expr(l, j)})",
                     f"{j} ({j:04b}) - {lb} = {nxt} ({nxt:04b}){fin}",
                     acc=f"{label} = {run - val} + {val} = {run}",
                     hold=2.2)
            self.play(FadeOut(conn), self.bit_box[j].animate.set_stroke(BLUE, 4),
                      run_time=0.4)
            kept.add(rect)            # dejamos el rectángulo para ver la unión
        return total, kept


# ============================================================
#  ESCENA 1: Introducción + idea del lowbit + llenado del árbol
# ============================================================
class S1_Intro(FenwickScene):
    def construct(self):
        self.setup_fenwick()

        # --- título ---
        title = Text("Fenwick Tree", font_size=56, weight=BOLD)
        sub = Text("(Binary Indexed Tree)", font_size=32, color=GREY_B).next_to(title, DOWN)
        self.play(Write(title), run_time=1.0)
        self.play(FadeIn(sub, shift=UP * 0.3), run_time=0.6)
        self.wait(0.8)
        small = Text("Fenwick Tree: sumas parciales inteligentes",
                     font_size=34).move_to([0, 3.45, 0])
        self.play(ReplacementTransform(VGroup(title, sub), small), run_time=0.8)
        self.title = small

        # --- el problema ---
        self.show_array(run_time=1.8)
        self.say(f"Problema: A[1] + ... + A[6] = {self.expr(1, 6)} = {sum(ARR[:6])}",
                 "sumarlos uno por uno cuesta O(n) por cada consulta", hold=2.0)
        self.play(LaggedStart(*[Indicate(self.arr_box[i], color=RED, scale_factor=1.15)
                                for i in range(1, 7)], lag_ratio=0.35), run_time=2.4)
        self.say("Con muchas consultas y cambios, esto es muy lento",
                 "idea: guardar sumas parciales de tamaño potencia de 2", hold=2.2)

        # --- fila del árbol (vacía) ---
        self.show_bit(filled=False, run_time=1.6)

        # --- el truco: lowbit ---
        lines = VGroup(
            Text("i       = 0110   (6)", font_size=26, font="Monospace"),
            Text("-i      = 1010", font_size=26, font="Monospace"),
            Text("i & -i  = 0010   (lowbit = 2)", font_size=26, font="Monospace", color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([0, 0.45, 0])
        box = SurroundingRectangle(lines, buff=0.12, color=YELLOW)
        self.say("lowbit(i) = el bit 1 más pequeño de i",
                 "tree[i] guarda la suma de los últimos lowbit(i) elementos", hold=1.8)
        self.play(LaggedStart(*[Write(l) for l in lines], lag_ratio=0.6),
                  Create(box), run_time=2.6)
        cov6 = self.cover(6, YELLOW)
        self.play(Create(cov6), self.bit_box[6].animate.set_stroke(YELLOW, 6), run_time=0.8)
        self.say(f"Ejemplo: lowbit(6) = 2  ->  tree[6] cubre A[5..6] = {self.expr(5, 6)}",
                 hold=2.6)
        self.play(FadeOut(lines), FadeOut(box), FadeOut(cov6),
                  self.bit_box[6].animate.set_stroke(BLUE, 4), run_time=0.8)

        # --- rellenar el árbol celda por celda ---
        for i in range(1, self.n + 1):
            lb = i & -i
            l = i - lb + 1
            rect = self.cover(i, YELLOW)
            conn = self.connector(i, rect, YELLOW)
            self.play(Create(rect), Create(conn), run_time=0.5)
            if lb == 1:
                msg = f"tree[{i}] = A[{i}] = {self.fw.t[i]}"
            else:
                msg = f"tree[{i}] = {self.rng(l, i)} = {self.expr(l, i)} = {self.fw.t[i]}"
            self.say(msg, f"lowbit({i}) = {lb}  ->  cubre {lb} elemento(s)",
                     extra=[self.bit_box[i].animate.set_fill(BLUE_E, 0.6),
                            Write(self.bit_txt[i])],
                     hold=2.0 if i == self.n else 1.2, run_time=0.6)
            self.play(FadeOut(rect), FadeOut(conn), run_time=0.3)

        self.say("Cada celda i resume lowbit(i) elementos",
                 "con esto, sumar y actualizar cuesta O(log n)", hold=2.0)


# ============================================================
#  ESCENA 2: update(i, delta)
# ============================================================
class S2_Update(FenwickScene):
    def construct(self):
        self.setup_fenwick()
        self.set_title("Operación 1: update(i, delta)")
        self.show_array()
        self.show_bit()
        self.wait(0.3)
        self.say("Si cambia A[3], cambian todas las celdas que la cubren",
                 "¿cuáles? las que encontramos saltando con i + lowbit(i)", hold=2.2)
        self.animate_update(3, 4)          # A[3] pasa de 5 a 9
        self.wait(1)


# ============================================================
#  ESCENA 3: query(i)  (suma de prefijo)
# ============================================================
class S3_Query(FenwickScene):
    def construct(self):
        self.setup_fenwick()
        self.set_title("Operación 2: query(i) = A[1] + ... + A[i]")
        self.show_array()
        self.show_bit()
        self.wait(0.3)
        self.say(f"Queremos A[1] + ... + A[6] = {self.expr(1, 6)}",
                 "en vez de sumar 6 números, sumamos pocas celdas del árbol", hold=2.5)
        total, kept = self.animate_query(6, None, "suma")
        self.say(f"Resultado: {total}   ({len(kept)} lecturas en vez de 6)",
                 f"comprobación: {self.expr(1, 6)} = {sum(ARR[:6])}",
                 acc=f"suma = {total}", hold=3.0)


# ============================================================
#  ESCENA 4: suma en un rango [l, r]
# ============================================================
class S4_RangeQuery(FenwickScene):
    def construct(self):
        self.setup_fenwick()
        self.set_title("Operación 3: suma en rango [l, r]")
        self.show_array()
        self.show_bit()
        l, r = 3, 6
        target = self.span_rect(l, r, GREEN)
        self.say(f"Queremos A[{l}] + ... + A[{r}] = {self.expr(l, r)}",
                 f"truco: suma({l}..{r}) = prefijo({r}) - prefijo({l - 1})", hold=2.5)
        self.play(Create(target), run_time=0.8)

        p_r, k1 = self.animate_query(r, BLUE, f"prefijo({r})")
        self.say(f"prefijo({r}) = {p_r}, pero incluye de más A[1..{l - 1}]",
                 f"hay que restar prefijo({l - 1})", hold=2.0)
        p_l, k2 = self.animate_query(l - 1, RED, f"prefijo({l - 1})")

        res = p_r - p_l
        assert res == self.fw.range_query(l, r) == sum(ARR[l - 1:r])
        self.say(f"{p_r} - {p_l} = {res}", "lo que sobra es justo el rango pedido",
                 acc=f"suma[{l}..{r}] = {res}", hold=2.5)
        self.play(FadeOut(k1), FadeOut(k2), run_time=0.6)
        self.play(Indicate(target, color=GREEN, scale_factor=1.1), run_time=0.8)
        self.wait(1)