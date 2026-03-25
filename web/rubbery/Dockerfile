FROM alpine:20260127

ENV FLAG=dctf{this_is_a_test_flag}

WORKDIR /srv

RUN echo 'https://dl-cdn.alpinelinux.org/alpine/edge/testing' >> /etc/apk/repositories

RUN apk add python3 uv tectonic pdf2svg

COPY chall/pyproject.toml chall/uv.lock ./
RUN uv sync --no-build

# Force tectonic to pre-cache 
RUN tectonic - -o /tmp <<'EOF'
\documentclass[preview]{standalone}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}
\thispagestyle{empty}
\begin{document}
$$
\mathbf{V}_1 \times \mathbf{V}_2 =  \begin{vmatrix}
\mathbf{i} & \mathbf{j} & \mathbf{k} \\
\frac{\partial X}{\partial u} &  \frac{\partial Y}{\partial u} & 0 \\
\frac{\partial X}{\partial v} &  \frac{\partial Y}{\partial v} & 0
\end{vmatrix}
$$
\end{document}
EOF

COPY chall/ .

CMD PORT=8000 uv run main.py
