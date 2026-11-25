import os, numpy as np, pyarrow as pa, pyarrow.parquet as pq, rasterio
from rasterio.windows import Window

SRC, OUT, STRIDE, ROWS = "data/raw/2025_30m_cdls.tif", "data/parquet/pixels", 4, 1024
os.makedirs(OUT, exist_ok=True)
with rasterio.open(SRC) as ds:
    print(ds.crs, ds.width, ds.height)  # note these for the README
    T = ds.transform
    for r0 in range(0, ds.height, ROWS):
        h = min(ROWS, ds.height - r0)
        a = ds.read(1, window=Window(0, r0, ds.width, h))[::STRIDE, ::STRIDE]
        rr, cc = np.nonzero(a)  # drop 0 = background/NoData
        if rr.size == 0:
            continue
        x = T.c + (cc * STRIDE + 0.5) * T.a  # pixel-center coords (meters, Albers)
        y = T.f + (r0 + rr * STRIDE + 0.5) * T.e
        pq.write_table(
            pa.table(
                {
                    "x": x.astype("int32"),
                    "y": y.astype("int32"),
                    "crop_code": a[rr, cc].astype("int16"),
                }
            ),
            f"{OUT}/part-{r0:06d}.parquet",
        )
