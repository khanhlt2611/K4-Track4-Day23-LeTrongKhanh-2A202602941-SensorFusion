# Báo cáo bài nộp — Day 23 Sensor Fusion Lab

## Thông tin học viên

- Họ tên: Lê Trọng Khánh
- MSSV: 2A202602941
- Email: letrongkhanh26112004@gmail.com
- Link repo (fork): https://github.com/khanhlt2611/K4-Track4-Day23-LeTrongKhanh-2A202602941
- Commit hash nộp (`git rev-parse HEAD`): Chưa chốt. Sau khi commit code, artifacts và báo cáo, lấy hash commit cuối bằng `git rev-parse HEAD` để nộp trên LMS. HEAD hiện tại chưa chứa bài làm nên không dùng làm hash nộp.

## Tóm tắt kết quả

Số liệu lấy từ [metrics.json](artifacts/metrics.json) và đối chiếu với [grade_run.log](artifacts/grade_run.log), không sửa tay artifacts.

- `fusion_mode`: `compare`.
- `frames`: `[0, 198]`, tính cả hai đầu, tổng cộng 199 frame cho mỗi mode.
- `segment`: `training_segment-1005081002024129653_5313_150_5333_150_with_camera_labels.tfrecord`.
- `seed`: `0`.
- Detection: `precision = 0.9700934579439252`, `recall = 0.7004048582995951`, `tp = 519`, `fp = 16`, `fn = 222`.

| Chỉ số tracking | LiDAR | LiDAR + camera (fused) |
|---|---:|---:|
| `rmse` (m) | 0.15032268781360134 | 0.13586678833539081 |
| `matches` | 502 | 502 |
| `sum_sq_err` (m²) | 11.343649056695735 | 9.266811654632093 |
| `ghost_track_frames` | 0 | 0 |
| `missed_gt_frames` | 239 | 239 |
| `mean_confirmed_tracks` | 2.522613065326633 | 2.522613065326633 |
| `precision_track = matches / (matches + ghost_track_frames)` | 1.0 | 1.0 |
| `coverage = matches / detection.tp` | 0.9672447013487476 | 0.9672447013487476 |

### Nhận xét hai mode

Fused giảm RMSE từ 0.150323 m xuống 0.135867 m, tương đương giảm 0.014456 m, khoảng 9.62%. Hai mode đều có 502 cặp ghép, 0 ghost và 239 miss. Như vậy, cải thiện RMSE đi cùng số lượng cặp ghép giữ nguyên; không có dấu hiệu giảm sai số chỉ bằng cách bỏ bớt cặp ghép. Số liệu tổng hợp cho thấy camera cải thiện độ chính xác vị trí, còn số lượng confirmed tracks và các chỉ số ghép tổng thể không thay đổi. Không thể từ các tổng này kết luận danh tính mọi cặp ghép ở hai mode đều giống nhau.

Ví dụ trong `grade_run.log`, frame 131 ở cả hai mode có `confirmed = matches = 3`, `ghosts = misses = 0`. `sum_sq_err` giảm từ 0.12303751286510352 m² ở LiDAR xuống 0.0580531834297013 m² ở fused. Camera không nhất thiết cải thiện từng frame: tại frame 4, với cùng 2 matches, sai số bình phương tổng của fused là 0.03198731678441609 m², cao hơn LiDAR là 0.011281520740472877 m². Kết luận cải thiện áp dụng cho RMSE của cả segment.

239 miss là tổng số lần nhãn GT xe hợp lệ không ghép được với confirmed track qua các frame, không phải 239 xe riêng biệt. Các nguyên nhân có thể gồm detector bỏ sót, track chưa confirmed hoặc ghép đo không thành công. Log có 222 detection FN; ở frame 0–3, mỗi mode có 2 detection TP nhưng chưa có confirmed track nên mỗi frame vẫn có 2 miss. Điều này minh họa việc detection đúng chưa đồng nghĩa với tracking đã xác nhận. Coverage trong rubric dùng `matches / det_tp`, không dùng tổng GT làm mẫu số, nên coverage 96.72% không có nghĩa tracker bao phủ 96.72% tất cả nhãn GT.

Cả hai RMSE đều dưới 0.45 m; precision track 1.0 vượt 0.75; coverage 0.967245 vượt 0.70. `rmse_fused - rmse_lidar = -0.014455899478210521 m`, thỏa điều kiện fusion không xấu hơn quá 0.05 m. Đây là đối chiếu các ngưỡng chất lượng, không phải điểm cuối cùng của bài.

Camera trong lab dùng tâm hộp 2D ground-truth của camera FRONT có thêm nhiễu theo seed, không chạy camera detector. Do đó, kết quả này không chứng minh chất lượng của một camera detector hay một hệ thống perception độc lập với GT.

### Lệnh chạy và đối chiếu artifacts

Chạy từ gốc repo trong PowerShell, dùng `conda run` để chọn đúng Python của môi trường lab:

```powershell
conda run --no-capture-output -n day23_sensor_fusion python -m pytest student/tests -q
conda run --no-capture-output -n day23_sensor_fusion python -m fusion_lab.scripts.run_lab --config student/config/paths.yaml --fusion compare --seed 0
```

Cấu hình lần chạy: `frame_start: 0`, `frame_end: 198`. Kết quả test đã kiểm tra: **128 passed**, không còn `failed` hoặc `xfailed`.

Đã đối chiếu bằng `fusion_lab.evaluation.validate_metrics_records`: log gộp có đủ 398 record, một record cho mỗi `(mode, frame)`; các tổng trong metrics khớp log. Mỗi record thỏa `matches + ghosts == confirmed` và `matches + misses == valid_gt`. Các cặp metrics/log riêng cho LiDAR và fused cũng được kiểm tra nhất quán.

Sáu file của lần chạy nộp bài:

- `artifacts/metrics.json`
- `artifacts/grade_run.log`
- `artifacts/metrics_lidar.json`
- `artifacts/metrics_fused.json`
- `artifacts/grade_run_lidar.log`
- `artifacts/grade_run_fused.log`

Các file có hậu tố `_smoke_*` là lần thử 21 frame trước đó, không dùng làm số liệu báo cáo này.

## Giải thích ngắn (Parts E–H)

### 1. Khác biệt đo LiDAR 3D và camera 2D trong EKF (`z`, `R`)

Trạng thái EKF là `(px, py, pz, vx, vy, vz)`, kích thước 6×1. LiDAR đo vị trí 3D trong hệ sensor nên `z` có kích thước 3×1, đơn vị mét; `R` là ma trận 3×3 với phương sai đơn vị m². Mô hình đo LiDAR là phép biến đổi vị trí sang hệ sensor; Jacobian `H` có kích thước 3×6 và các cột vận tốc bằng 0.

Camera đo pixel `(u, v)` nên `z` có kích thước 2×1 và `R` là ma trận 2×2, đơn vị pixel². Trong [camera_fusion.py](workspace/camera_fusion.py), `build_camera_measurement` dùng `diag(sigma_cam_i², sigma_cam_j²)`; với tham số hiện tại, cả hai phương sai là 25 pixel². Camera dùng phép chiếu pinhole phi tuyến: đổi vị trí sang hệ sensor rồi tính `u = c_i - f_i*y_s/x_s`, `v = c_j - f_j*z_s/x_s`. `H` là Jacobian 2×6 do platform tính. Camera không đo trực tiếp độ sâu hay vận tốc.

Trong [kalman.py](workspace/kalman.py), hai loại đo cùng dùng `gamma = z - h(x)`, `S = HPHᵀ + R`, `K = PHᵀS⁻¹` để hiệu chỉnh. Code giải hệ tuyến tính để tính gain thay vì lập nghịch đảo tường minh. Bước predict dùng mô hình vận tốc không đổi với `dt = 0.1 s`; `Q = dt*q*I₆` là mô hình nhiễu đường chéo riêng của lab.

### 2. Vì sao cần gating Mahalanobis trước khi gán?

Mahalanobis dùng `d² = gammaᵀS⁻¹gamma`, nên đánh giá residual theo độ không chắc chắn của track và phép đo. Cùng một khoảng cách Euclidean có thể hợp lý khi covariance lớn nhưng không hợp lý khi covariance nhỏ. Gating loại cặp khó có khả năng thuộc cùng một xe, giảm nguy cơ ghép nhầm và làm lệch trạng thái EKF.

Trong [association.py](workspace/association.py), `chi2_gate` so sánh `d²` với `chi2.ppf(gating_threshold, sensor.dim_meas)`, dùng `gating_threshold = 0.995` và số chiều đo 3 cho LiDAR, 2 cho camera. `association_cost_matrix` kiểm tra FOV trước khi tính Mahalanobis; cặp ngoài FOV hoặc ngoài gate có cost `inf`. Cách này cũng tránh chiếu camera với điểm sau camera hoặc có độ sâu không hợp lệ. `pick_next_pair` chỉ chọn cost hữu hạn nhỏ nhất rồi xóa hàng/cột để mỗi track và phép đo được ghép tối đa một lần trong lượt sensor đó.

### 3. Pipeline là track-then-fuse hay fuse-then-track?

Pipeline là **track-then-fuse**, với một tracker: mỗi frame predict các track một lần, gán và update LiDAR, sau đó gán và update camera lên trạng thái vừa được LiDAR cập nhật. Không có bước trộn các detection LiDAR/camera thành một phép đo chung trước khi tracking.

Bằng chứng thứ tự nằm trong `run` của [run_lab.py](../platform/fusion_lab/scripts/run_lab.py): vòng lặp `KF.predict(track)` chạy trước `associate_and_update(..., lidar_sensor)`, rồi đến `associate_and_update(..., camera_sensor)` khi có nhãn camera FRONT. Log `grade_run.log` ghi kết quả theo `(mode, frame)`, không ghi từng thao tác predict/update, nên không thể dùng riêng log để chứng minh thứ tự nội bộ. Log xác nhận cả hai mode được chạy trên frame 0–198; ví dụ frame 131 có 3 matches ở cả hai mode nhưng sai số fused nhỏ hơn. Thứ tự fusion được đối chiếu bằng code runner.

### 4. Nếu camera lệch calibration, triệu chứng gì trên innovation/residual?

Extrinsic hoặc intrinsics sai làm pixel dự đoán `h(x)` lệch khỏi phép đo. Innovation `z - h(x)` có thể mang độ lệch có hệ thống theo hướng hoặc vị trí xe, thay vì chỉ dao động quanh 0 do nhiễu. Sai lệch đủ lớn làm Mahalanobis vượt gate và phép đo camera bị loại. Nếu sai lệch còn nằm trong gate, EKF vẫn cập nhật và có thể kéo vị trí/vận tốc về ước lượng sai, làm RMSE fused tăng.

FOV và Jacobian cũng phụ thuộc calibration, nên calibration sai có thể làm đánh giá visibility hoặc gain cập nhật không phù hợp. Đây là phân tích từ mô hình đo và gating; bài này chưa thực hiện thí nghiệm làm lệch calibration. `grade_run.log` không lưu innovation, nên không suy ra một giá trị residual cụ thể từ log đã nộp.

### 5. Vì sao cần sensor tường minh ở frame rỗng? Vì sao LiDAR quyết định score/init/delete?

Khi `meas_list` rỗng, không thể lấy loại sensor từ phần tử đầu tiên. Tham số `sensor` vẫn cho biết đây là lượt LiDAR hay camera, để `associate_and_update` luôn gọi `manager.manage_tracks(unassigned_tracks, unassigned_meas, sensor)` đúng chính sách.

Ở lượt LiDAR rỗng, các track chưa ghép nhưng trong FOV cần bị trừ score và xét xóa. Bỏ qua lượt này sẽ giữ lại các track không còn được quan sát. Ngược lại, camera rỗng hoặc không ghép được không được làm giảm score. LiDAR cung cấp vị trí 3D để khởi tạo; camera 2D chỉ bổ sung ràng buộc vị trí lên track đã tồn tại. Lab chọn LiDAR làm nguồn quyết định tồn tại, tránh việc thiếu nhãn hoặc FOV camera làm thay đổi vòng đời track.

Trong [association.py](workspace/association.py), cặp ghép được update EKF rồi chuyển tới `handle_updated_track(track, sensor)`. [TrackManager](../platform/fusion_lab/tracking/manager.py) chỉ tăng score khi `sensor.name == 'lidar'`; `manage_tracks` trả về ngay với sensor camera, nên camera không tạo, trừ score hoặc xóa track. Các test cũng kiểm tra camera có thể tinh chỉnh vị trí mà không đổi score hay state.

### 6. Điều kiện xác nhận, giữ confirmed sau miss và xóa track

Trong [track_management.py](workspace/track_management.py), track mới được khởi tạo từ LiDAR với vị trí đổi sang hệ vehicle, vận tốc bằng 0, state `initialized` và score `1/window = 1/6`. Covariance vị trí là `R` đo xoay sang hệ vehicle; covariance vận tốc dùng bình phương `sigma_p44`, `sigma_p55`, `sigma_p66`.

Mỗi LiDAR hit tăng score thêm `1/6`, giới hạn tối đa 1. Track chưa confirmed có hit chuyển sang `tentative`; khi `score > confirmed_threshold = 0.8`, chuyển sang `confirmed`. Dấu so sánh là `>`, nên score đúng 0.8 chưa đủ xác nhận. LiDAR miss trong FOV trừ `1/6`; miss không hạ state của track đã confirmed. Ngoài FOV LiDAR không tính miss score, nhưng lượt LiDAR vẫn xét điều kiện xóa theo covariance.

Xóa track nếu **một trong** các điều kiện sau đúng: `Pxx > max_P` hoặc `Pyy > max_P` với `max_P = 9 m²`; track confirmed có `score < delete_threshold = 0.6`; track chưa confirmed có `score <= 0`. Score đúng 0.6 và variance đúng 9 chưa đủ kích hoạt hai ngưỡng tương ứng. Camera không áp dụng các quyết định vòng đời này.

Log phù hợp với chính sách xác nhận: frame 0–3 của cả hai mode có 2 detection TP nhưng 0 confirmed track; đến frame 4 có 2 confirmed tracks và 2 matches, sau năm quan sát LiDAR liên tiếp.

## Bonus (không bắt buộc)

- Không. Chưa thực hiện export CVAT, trực quan hóa hoặc thí nghiệm lệch calibration để xin điểm bonus.

## Khai báo sử dụng AI (bắt buộc)

- Công cụ đã dùng (ChatGPT, Copilot, Claude, …): Codex / ChatGPT (OpenAI).
- Dùng cho phần nào (hàm, câu hỏi, debug): AI đọc tài liệu và code dự án, xác định các công việc cần làm; sửa đường dẫn dữ liệu; chẩn đoán xung đột OpenMP và chuyển backend BLAS sang OpenBLAS; triển khai đủ 17 hàm Part E, G, F, H; hướng dẫn lệnh chạy; soạn báo cáo, giải thích thuật toán và tính các chỉ số phụ từ artifacts thật. Code E–H và nội dung báo cáo có hỗ trợ trực tiếp từ AI.
- Cách bạn đã kiểm tra lại (pytest, chạy Waymo, đối chiếu công thức): Trong phiên làm việc, AI chạy toàn bộ test và thu được 128 passed; kiểm tra phép toán NumPy/SciPy/PyTorch; chạy thử hai mode trên 21 frame. Học viên chạy lần nộp bài trên 199 frame với `compare`, `seed 0`. AI đối chiếu metrics/log gộp và từng mode bằng validator, kiểm tra đủ 398 record và các đẳng thức đếm. Các công thức EKF, Mahalanobis, chiếu camera và ngưỡng vòng đời được đối chiếu với hướng dẫn, tham số và code platform. Số liệu báo cáo lấy từ lần chạy 199 frame, không tạo giả hoặc sửa artifacts. Học viên cần tự rà lại code và các câu giải thích để có thể trình bày khi vấn đáp.

## Checklist nộp

- [x] Part E–H đã implement; test có 128 passed, không còn failed/xfailed.
- [x] Part A–D và code platform giữ nguyên.
- [x] Lần chạy chấm điểm: `compare`, seed 0, frame 0–198.
- [ ] Đã commit đủ 6 file metrics/log của lần chạy chấm điểm (hiện đã sinh nhưng chưa commit).
- [ ] Hoàn tất thông tin nộp: cập nhật commit hash cuối; báo cáo số liệu, 6 câu giải thích và khai báo AI đã điền.
- [x] Dữ liệu Waymo, weights, `paths.yaml` và `.env` không nằm trong danh sách file Git theo dõi tại lúc kiểm tra.
- [ ] Checker báo `KẾT QUẢ: SẴN SÀNG NỘP` sau khi commit các thay đổi.
- [ ] Đã push và nộp link repo + commit hash lên LMS.

Lệnh kiểm tra sau khi commit:

```powershell
conda run --no-capture-output -n day23_sensor_fusion python -X utf8 tools/check_submission.py
```
