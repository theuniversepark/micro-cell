"""정밀조립존 OCS Cell (Local Server – Edge Gateway Server 데이터 계층) 구성·토폴로지 페이지 → ocs_precision.html"""
import re
import html
import build_page as bp
from privacy import out
from cells_data import ZONE, CELLS
from ocs_pz_products import P, SRC, BASIS, FX, USE, CELL_HW, CELL_SW, CELL_P, CELL_SRC

E = html.escape
CSS = re.search(r"<style>.*?</style>", bp.page(), re.S).group(0)

# ------------------------------------------------------------------ 데이터량 산정 (장비 단위 상향식)
# 셀 기준 장비 (사용자 지정 2026-10-07): 협동로봇 10 + AMR 4 + AMMR 양팔 1 = 로봇 15대, 로봇별 카메라 3대(손목 D405 · 머리·가슴 D455) + 협동로봇 엑소센트릭 D455 1대, 모두 USB3로 로봇 엣지 직결 (2026-10-08 엑소 추가)
OPS_H = 8 * 22          # 월 운용시간: 일 8h × 22일, 운용 중 연속 기록 (가정)
ROBOTS = [("협동로봇", 10), ("AMR", 4), ("AMMR 양팔로봇", 1)]
N_ROBOT = sum(n for _, n in ROBOTS)
# 카메라 스트림 (Mbps)
CAMS = [
    ("손목 카메라 (RealSense D405)", "RGB 1280×720 · 30fps · H.265 4Mbps + Depth 640×480 · 15fps · 16bit 무손실 압축(약 4:1) 18.4Mbps", 4 + 640 * 480 * 2 * 15 / 4 * 8 / 1e6,
     "협동로봇·AMMR 손목, AMR은 도킹부 · USB3 엣지 직결"),
    ("머리 카메라 (RealSense D455)", "RGB 1280×800 · 30fps · H.265 4Mbps + Depth 640×480 · 15fps · 16bit 무손실 압축(약 4:1) 18.4Mbps", 4 + 640 * 480 * 2 * 15 / 4 * 8 / 1e6,
     "작업영역 상부 시점 · USB3 엣지 직결"),
    ("가슴 카메라 (RealSense D455)", "RGB 1280×800 · 30fps · H.265 4Mbps + Depth 640×480 · 15fps · 16bit 무손실 압축(약 4:1) 18.4Mbps", 4 + 640 * 480 * 2 * 15 / 4 * 8 / 1e6,
     "로봇 정면 행동·작업자 근접 · USB3 엣지 직결"),
]
CAM_MBPS = sum(c[2] for c in CAMS)
# 협동로봇만 추가하는 엑소센트릭(3인칭 고정 시점) 카메라 — 로봇 행동 데이터 수집
EXO = ("엑소센트릭 카메라 (RealSense D455)", "RGB 1280×800 · 30fps · H.265 4Mbps + Depth 640×480 · 15fps · 16bit 무손실 압축(약 4:1) 18.4Mbps", 4 + 640 * 480 * 2 * 15 / 4 * 8 / 1e6,
       "협동로봇만 1대씩 · 1.5~2m 고정 폴·천장 마운트 · 액티브 USB3로 로봇 엣지 직결")
N_EXO = dict(ROBOTS)["협동로봇"]
N_CAM = N_ROBOT * len(CAMS) + N_EXO
CAM_CELL = N_ROBOT * CAM_MBPS + N_EXO * EXO[2]
# 로봇 텔레메트리 (B/s)
TEL = [
    ("협동로봇", "관절 7축(위치·속도·토크·전류, float32) 100Hz 11.2KB/s + TCP 포즈 100Hz 2.8KB/s + 6축 F/T 1kHz 24KB/s + 그리퍼·상태 이벤트 1KB/s",
     7 * 4 * 4 * 100 + 7 * 4 * 100 + 6 * 4 * 1000 + 1000),
    ("AMR", "주행 상태(포즈·속도·배터리·임무) 20Hz 4KB/s + 2D LiDAR 2대(25Hz · 1,081점 · 거리+강도 16bit) 216KB/s + IMU 200Hz 4.8KB/s",
     200 * 20 + 2 * 25 * 1081 * 4 + 6 * 4 * 200),
    ("AMMR 양팔로봇", "양팔 14축 100Hz 22.4KB/s + TCP 포즈 2개 5.6KB/s + F/T 2개 1kHz 48KB/s + 이동부(AMR과 동일) 225KB/s",
     14 * 4 * 4 * 100 + 2 * 7 * 4 * 100 + 2 * 6 * 4 * 1000 + (200 * 20 + 2 * 25 * 1081 * 4 + 6 * 4 * 200)),
]
TEL_BPS = {t[0]: t[2] for t in TEL}


def tb_month(mbps):  # Mbps 연속 → TB/월 (10진 TB)
    return mbps / 8 * 3600 * OPS_H / 1e6


def sizing():
    rows = []
    for c in CELLS:
        cam_n = N_CAM
        cam_mbps = CAM_CELL
        tel_mbps = sum(n * TEL_BPS[name] for name, n in ROBOTS) * 8 / 1e6
        rows.append(dict(id=c["id"], rob=N_ROBOT, cam=cam_n, cam_mbps=cam_mbps, tel_mbps=tel_mbps,
                         video=tb_month(cam_mbps), tel=tb_month(tel_mbps), tot=tb_month(cam_mbps + tel_mbps),
                         tags=N_ROBOT * 400 + cam_n * 50 + 1200))
    return rows


SZ = sizing()
MONTH_TB = sum(r["tot"] for r in SZ)
RET_M = 3                 # 로컬 보관 개월
FILL = 0.8                # Ceph 권장 최대 사용률
AIR_RATIO = 0.2          # AI Ready 데이터 = 원시 대비 최대 20% (상한 적용)
AIR_RET = 3              # AI Ready 로컬 보관 개월
RAW_TB = MONTH_TB * RET_M
AIR_TB = MONTH_TB * AIR_RATIO * AIR_RET
NEED_TB = (RAW_TB + AIR_TB) * 1.3          # 메타데이터·복제 외 여유 1.3
NEED_1M = (MONTH_TB + MONTH_TB * AIR_RATIO) * 1.3
NODE_RAW = 240            # 12 × 20TB
NODE_USABLE = NODE_RAW * 4 / 6            # 이레이저 코딩 4+2
N_STO = max(6, -(-int(NEED_TB / FILL) // int(NODE_USABLE)))
LOAD_KW = 2.4 + 4.0 + N_STO * 0.5 + 1.3
N_UPS = max(1, -(-int(LOAD_KW * 10) // 128))          # 20kVA(16kW) UPS를 80% 이하로 운용
N_RACK = 2 + -(-(N_STO * 2) // 36)                     # 스토리지 랙은 36U까지 채움(PDU·배터리 여유)
DAILY_TB = (CAM_CELL + 0) / 8 * 3600 * 8 / 1e6         # 셀 영상 1일(8h) 발생량
BUF_D = int(24 / DAILY_TB)                              # 영상 수집 노드 HDD 24TB(RAID1) 버퍼 일수
NEED = {3: NEED_TB}


# 스토리지 노드 수에 따라 달라지는 수량 근거
BASIS["STO"] = (f"필요 {NEED_TB:,.0f}TB(원시 {RAW_TB:,.0f}TB + AI Ready {AIR_TB:,.0f}TB, × 1.3) ÷ Ceph 권장 사용률 80% = usable {NEED_TB / FILL:,.0f}TB ÷ 노드당 usable "
                f"{NODE_USABLE:.0f}TB(raw 240TB × 이레이저 코딩 4+2) = {NEED_TB / FILL / NODE_USABLE:.1f} → {N_STO}대")
BASIS["CORE"] = (f"MLAG 이중화 2대. 소요 포트 약 {6 + 4 + N_STO * 4 + 20 + 5}개(로컬 서버 6, GPU 4, 스토리지 {N_STO * 4}[{N_STO}노드×공용망·클러스터망], 셀 액세스 업링크 20, "
                 f"백업·방화벽·관제·관리 5)를 2대에 나누면 대당 약 {(6 + 4 + N_STO * 4 + 20 + 5 + 1) // 2}포트 ≤ 48")
BASIS["UPS"] = (f"서버실 부하 산정 약 {LOAD_KW:.1f}kW(서버 2.4 + GPU 서버 4.0 + 스토리지 {N_STO}노드 {N_STO * 0.5:.1f} + 네트워크·기타 1.3) → 20kVA(16kW)를 부하율 80% 이하로 쓰면 "
                f"{N_UPS}대(병렬), 30분 유지")
BASIS["CRAC"] = f"서버실 열부하 약 {LOAD_KW:.0f}kW → 20kW급 1대(여유 포함)"
BASIS["RACK"] = (f"Rack A(연산: 로컬 서버 3·GPU 서버 2 = 14U) + Rack B(코어·방화벽·관리·백업·PTP) + 스토리지 {N_STO}노드 {N_STO * 2}U를 랙당 36U까지 → "
                 f"스토리지 랙 {N_RACK - 2}대, 합계 {N_RACK}대")
BASIS["VNODE"] = (f"셀당 1대 × 5. 셀 카메라 {N_CAM}대(로봇 {N_ROBOT}대 × 3 + 협동로봇 엑소 {N_EXO}) 영상 평균 {CAM_CELL:,.0f}Mbps(로봇 엣지 업로드)를 받아 NVMe에 수신 → "
                  f"HDD 24TB(RAID1)에 약 {BUF_D}일분(하루 8h 기준 {DAILY_TB:.1f}TB/일) 버퍼 → Data Lake로 업로드. L4 디코더 4개로 영상 AI(작업자 접근 감지 등) 처리. 10GbE 2포트를 셀 액세스 스위치 2대에 1회선씩 연결")


# ------------------------------------------------------------------ 장비 목록
# (계층, 기호, 품목, 주요 스펙, q1, q2, q3, 단위, 용도, 설치 위치)
HW = [
    ("Local Server", "LS", "로컬 서버 노드 (K8s HA 클러스터)", "2U · Xeon 6 P-core 2소켓(코어 32×2급) · RAM 512GB · NVMe 2×7.68TB · 25GbE×2(OCP 3.0)", 3, 0, 0, "대",
     "AAS Repository·Operational TSDB·Feature Store·OCS·AI Ready 변환 파이프라인 실행 (3노드 HA)", "존 서버실 Rack A"),
    ("Local Server", "GPU", "GPU 서버 (GPU-1 실시간 추론 · GPU-2 배치)", "4U · 2×AMD EPYC · RTX PRO 6000 96GB×4 (8장까지 증설) · RAM 512GB · NVMe 15TB", 2, 0, 0, "대",
     "GPU-1: AI Inference Engine(Triton) 실시간 추론 / GPU-2: AI Ready 변환 GPU 단계·영상 비식별·사전 라벨링·합성데이터·재학습", "존 서버실 Rack A"),
    ("Local Server", "STO", "Scale-out 스토리지 노드 (S3 + NFS)", "12×20TB HDD(raw 240TB) + NVMe 캐시 · 이레이저 코딩 4+2 · 25GbE×4(공용망·클러스터망)", N_STO, 0, 0, "노드",
     f"Data Lake — raw 버킷(원시 {RET_M}개월) + ai-ready 버킷(AI Ready {AIR_RET}개월) (필요 {NEED_TB:,.0f}TB)", "존 서버실 Rack C"),
    ("Local Server", "BAK", "백업 NAS", "usable 50TB · 스냅샷 · 오프사이트 복제", 1, 0, 0, "대",
     "AAS·TSDB·설정·모델 백업 (원시데이터 원본은 중앙 Golden Copy)", "존 서버실 Rack B"),
    ("Edge Gateway", "EGW", "Edge Gateway Server", "산업용 박스형 · Core i9급 24코어 · RAM 64GB · GPU(RTX 2000 Ada) 1 · NVMe 4TB · 10GBASE-T 1 + 2.5GbE 2", 6, 0, 0, "대",
     "셀 단위 OPC UA 수집·정규화·AAS 매핑, 엣지 TSDB(시계열 7일 버퍼), F/T 이상감지 모델, 설정·모델 배포 수신", "각 셀 네트워크 캐비닛"),
    ("Edge Gateway", "VNODE", "영상 수집 노드", "Short-Depth 엣지 서버 · Xeon 6 · RAM 128GB · NVIDIA L4(NVDEC 4) · U.2 NVMe 3.84TB×2(RAID1, 수신) + 24TB HDD×2(RAID1, 영상 버퍼) · 10GbE×2", 5, 0, 0, "대",
     f"셀 카메라 {N_CAM}대 영상 수신·버퍼·Data Lake 업로드, 영상 AI(작업자 접근 감지) 추론", "각 셀 네트워크 캐비닛"),
    ("Edge Gateway", "CAB", "셀 네트워크 캐비닛", "18U · 전면 잠금 · 팬 · 1kVA 라인인터랙티브 UPS · 광 패치", 5, 0, 0, "식",
     "EGW·셀 스위치 설치, 셀 단위 전원 보호", "각 셀 출입구 측 벽면"),
    ("네트워크·시간동기", "CORE", "코어 스위치 (L3)", "48×25GbE + 6×100GbE · MLAG 이중화 · PTP 지원", 2, 0, 0, "대",
     "서버·스토리지·셀 캐비닛 집선, 존 백본", "존 서버실 Rack B"),
    ("네트워크·시간동기", "TSN", "셀 TSN 산업용 스위치", "관리형 · 6×GbE + 2×GbE/SFP 콤보 · IEEE 802.1AS·1588 · TSN(Qbv)", 20, 0, 0, "대",
     "PLC·로봇 컨트롤러·온디바이스 엣지·EGW 연결, μs급 시간동기 분배 (셀당 4대)", "각 셀 캐비닛"),
    ("네트워크·시간동기", "POE", "셀 액세스·PoE 스위치", "24×mGig(최대 10G) UPOE · 10G SFP+ 업링크 2(모듈)", 5, 0, 0, "대",
     "공정 비전 카메라·AP PoE 급전, 공정설비·제어 PC 연결, 서버실 10G 업링크 (셀당 1대)", "각 셀 캐비닛"),
    ("네트워크·시간동기", "MGT", "관리망 스위치", "48×1GbE · IPMI/BMC 전용", 1, 0, 0, "대",
     "서버 원격관리(IPMI)·장비 관리망 분리", "존 서버실 Rack B"),
    ("네트워크·시간동기", "FW", "산업용 방화벽 (OT/IT 경계)", "10GbE · HA 쌍 · DPI(OPC UA·MQTT) · VPN", 2, 0, 0, "대",
     "중앙 Server·TTA 검증 영역 연계 구간 보호, IEC 62443 Zone/Conduit 분리", "존 서버실 Rack B"),
    ("네트워크·시간동기", "PTP", "PTP 그랜드마스터", "GNSS 수신 · IEEE 1588 / 802.1AS 프로파일 · NTP · 홀드오버 OCXO", 1, 0, 0, "대",
     "로봇 100Hz·F/T 1kHz·영상 타임스탬프 정합 (타임싱크 서버 필수)", "존 서버실 Rack B + 옥상 안테나"),
    ("네트워크·시간동기", "AP", "산업용 Wi-Fi 6E AP", "로밍 50ms 이하 · PoE · 셀 내부·통로 천장", 7, 0, 0, "대",
     "AMR 4대·AMMR 1대(셀당) 무선 연결과 영상 업로드 (5G RU는 이음5G 별도)", "존 통로 천장"),
    ("네트워크·시간동기", "FIB", "광·UTP 배선 및 케이블 트레이", "셀 액세스 스위치–서버실 10G 이중 광(OM4) · Cat6A · 통로 상부 트레이", 1, 0, 0, "식",
     "셀 캐비닛–서버실 백본, 카메라·AP 배선", "존 통로 상부"),
    ("운영·DT", "OWS", "OCS 운영 워크스테이션", "i9 · 64GB · 듀얼 32″ 모니터", 2, 0, 0, "대",
     "1대 존 전체 관제(OCS·셀 상태·KPI) + 1대 셀 알람 대응(HOLD 승인·재배정)", "로컬존 DCC 관제실"),
    ("운영·DT", "DWS", "DT·시뮬레이션 워크스테이션", "Xeon W · 256GB · RTX PRO 6000 1 · NVMe 8TB", 2, 0, 0, "대",
     "1대 DMWorks 검증 DT(가상 시운전) + 1대 Isaac Sim 학습 DT(VLA·S2R), DT 리플레이", "로컬존 DCC 관제실"),
    ("운영·DT", "VW", "관제 비디오월", "55″ 베젤리스 2×2 · 영상 컨트롤러", 1, 0, 0, "식",
     "셀 영상·DT·KPI 대시보드 표시", "로컬존 DCC 관제실"),
    ("기반시설", "RACK", "서버 랙", "42U · 1,200mm 깊이 · 이중 PDU", N_RACK, 0, 0, "대",
     "Rack A 연산 · Rack B 네트워크·백업 · Rack C~ 스토리지", "존 서버실"),
    ("기반시설", "UPS", "UPS", "20kVA · 온라인 이중변환 · 30분 · 병렬 운전", N_UPS, 0, 0, "대",
     "서버실 전원 보호 (부하 약 13kW)", "존 서버실"),
    ("기반시설", "CRAC", "항온항습기", "냉방 15kW급 · 상부 취출", 1, 0, 0, "대",
     "서버실 열부하 처리", "존 서버실"),
    ("기반시설", "KVM", "KVM·콘솔", "8포트 IP-KVM · 랙 콘솔", 1, 0, 0, "식", "서버 현장 유지보수", "존 서버실 Rack A"),
]

SW = [
    ("Edge Gateway SW", "OPCUA", "OPC UA Aggregation Server", "수집·정규화·AAS 매핑 · OPC UA Client/Server · PubSub", 5, 0, 0, "카피",
     "필드장비 OPC UA 집약, 단위·명칭 정규화, AAS 서브모델 매핑"),
    ("Edge Gateway SW", "AASIM", "AAS 기반 OPC UA 정보모델", "OPC 30270(AAS Companion Spec) · 캠틱 정의 서브모델 · Semantic ID", 1, 0, 0, "식",
     "장비·공정·품질 데이터의 표준 정보모델 (존 공통, 셀별 인스턴스)"),
    ("Edge Gateway SW", "DRV", "필드장비 인터페이스 드라이버", "Modbus TCP · EtherNet/IP · 로봇 SDK · ROS2 브리지 · GigE Vision/RTSP", 3, 0, 0, "식",
     "PLC·로봇·카메라·F/T 이기종 프로토콜 연결"),
    ("Edge Gateway SW", "ETSDB", "엣지 TSDB 모듈", "시계열 DB(엣지판) · 다운샘플링 · store-and-forward", 6, 0, 0, "카피",
     "20ms/200ms/1~3s 주기 수집 버퍼, 통신 단절 시 보존"),
    ("Edge Gateway SW", "RAW", "원시데이터 수집·전송 모듈", "Vision·Vibration·Audio 대용량 · 청크 업로드 · 체크섬", 1, 0, 0, "식",
     "대용량 원시데이터를 Local Data Lake로 직접 적재 (OPC UA 경로 우회)"),
    ("Edge Gateway SW", "GWM", "Gateway 관리·Control 모듈", "AAS 기반 GW 설정 · 원격 배포(OTA) · 컨테이너(K3s) · 웹 클라우드 IF", 1, 0, 0, "식",
     "EGW 설정·상태·버전 일괄 관리, AI 모델 배포"),
    ("Edge Gateway SW", "EAI", "엣지 AI 런타임", "TensorRT·ONNX Runtime · 국산 NPU SDK", 6, 0, 0, "카피",
     "엣지 이상감지·영상 전처리 모델 실행"),
    ("Local Server SW", "K8S", "컨테이너 플랫폼", "Kubernetes HA · 레지스트리 · GitOps", 1, 0, 0, "식", "로컬 서비스 배포·이중화 운영"),
    ("Local Server SW", "AASR", "AAS Repository·Registry", "IEC 63278 · AAS API v3 · Eclipse BaSyx급", 1, 0, 0, "식",
     "존 내 모든 자산의 AAS 저장·조회, 중앙 Enterprise AAS와 동기화"),
    ("Local Server SW", "OTSDB", "Operational TSDB", "클러스터 3노드 · 초당 20만 포인트 · 12개월 보관", 1, 0, 0, "식",
     "운영 시계열(상태·알람·공정값) 저장·조회, DCC 대시보드 원천"),
    ("Local Server SW", "LAKE", "Data Lake 관리", "S3 버킷 · Apache Iceberg 테이블 · 셀/일자 Prefix", 1, 0, 0, "식",
     "Raw Data Store 구조화·버전 관리"),
    ("Local Server SW", "FS", "추론용 AI Feature Store", "온라인/오프라인 피처 · 시점 일치 조회", 1, 0, 0, "식",
     "엣지·로컬 추론에 같은 피처 제공"),
    ("Local Server SW", "INF", "AI Inference Engine", "NVIDIA Triton · 모델 버전 관리 · GPU/NPU 백엔드", 1, 0, 0, "식",
     "이상 판단·품질 판정·재계획 모델 추론 (이상 판단 10초 KPI)"),
    ("Local Server SW", "ETL", "AI Ready 변환 파이프라인", "워크플로 엔진 · 시간동기 정렬 · 정제 · AAS 매핑 · 품질검증(완전성·결측·시간정합성) · LeRobot/RLDS 변환", 1, 0, 0, "식",
     "원시데이터 → AI Ready 데이터셋 변환 후 중앙 전송"),
    ("Local Server SW", "MQTT", "MQTT 브로커 클러스터 + REST 게이트웨이", "MQTT 5 · Sparkplug B · TLS · 브리지", 1, 0, 0, "식",
     "중앙 Server 전송(MQTT 산업용 / REST 무선통신)"),
    ("Local Server SW", "CAT", "메타데이터 카탈로그·리니지", "데이터셋 ID·출처·수집조건·버전 추적", 1, 0, 0, "식",
     "order·cell_task·episode 공통 ID 추적, 데이터 재사용"),
    ("운영·DT SW", "OCS", "존 오케스트레이터 (OCS)", "Manufacturing Agent · Field Logistics Agent · Cell Agent API · 셀 재배정·HOLD", 1, 0, 0, "식",
     "셀 상태 집계·배치 진척·재계획, 공장 PA Agent 연계"),
    ("운영·DT SW", "DMW", "DMWorks (검증 DT)", "BASE + MULTIPLE PROCESS + PLC SIMULATION · 1카피", 1, 0, 0, "카피",
     "셀 공정·PLC 가상 시운전"),
    ("운영·DT SW", "ISAAC", "Isaac Sim·Lab (학습 DT)", "오픈 라이선스 · USD 씬", 1, 0, 0, "식", "VLA·스킬 학습 씬, S2R/R2S 정합"),
    ("운영·DT SW", "MON", "모니터링·로그", "메트릭·로그·알람 통합 (Prometheus/Grafana급)", 1, 0, 0, "식", "EGW·서버·파이프라인 상태 감시"),
    ("보안·검증 SW", "SEC", "보안 스택", "IAM·SSO · OPC UA 인증서 PKI · 접근통제 · 감사로그", 1, 0, 0, "식", "사용자·장비 인증, 데이터 접근권한"),
    ("보안·검증 SW", "TRC", "검증 연계 인터페이스 (TTA)", "명령/이벤트 Trace 수집 · Expected↔Actual Trace 비교 API", 1, 0, 0, "식",
     "플랫폼 상호운용성·제조데이터 표준·품질 검증 영역 연계"),
]


# ------------------------------------------------------------------ 논리 구성도
def logical_svg():
    o = ['<svg class="arch plan" viewBox="0 0 1140 822" role="img" aria-label="AAS 기반 수집–저장 공통 아키텍처 논리 구성도" style="max-width:1140px">',
         '<defs><marker id="m1" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--cyan)"/></marker>'
         '<marker id="m2" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#9DB8E8"/></marker></defs><g transform="translate(10,0)">']

    def band(y, h, title, sub, cls):
        o.append(f'<rect x="0" y="{y}" width="900" height="{h}" rx="6" class="ly {cls}"/>')
        o.append(f'<text x="14" y="{y + 28}" class="lyt">{E(title)}</text>')
        for i, s in enumerate(sub.split("|")):
            o.append(f'<text x="14" y="{y + 48 + i * 16}" class="lys">{E(s)}</text>')

    def boxes(y, items, h=56, x0=150, x1=890, cyl=False):
        n = len(items)
        bw = (x1 - x0 - (n - 1) * 10) / n
        for i, (t, s) in enumerate(items):
            x = x0 + i * (bw + 10)
            if cyl:
                o.append(f'<path d="M{x:.0f},{y + 8} v{h - 16} a{bw / 2:.0f},8 0 0 0 {bw:.0f},0 v-{h - 16} a{bw / 2:.0f},8 0 0 0 -{bw:.0f},0 a{bw / 2:.0f},8 0 0 0 {bw:.0f},0" class="box cyl"/>')
            else:
                o.append(f'<rect x="{x:.0f}" y="{y}" width="{bw:.0f}" height="{h}" rx="5" class="box"/>')
            o.append(f'<text x="{x + bw / 2:.0f}" y="{y + h / 2 + 2}" class="boxt">{E(t)}</text>')
            if s:
                o.append(f'<text x="{x + bw / 2:.0f}" y="{y + h / 2 + 18}" class="boxs">{E(s)}</text>')

    def arr(x1, y1, x2, y2, t, k="d", anchor="start", dx=8):
        o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="fl-{k}" marker-end="url(#{"m1" if k == "d" else "m2"})"/>')
        o.append(f'<text x="{x1 + dx}" y="{(y1 + y2) / 2 + 4}" class="fl-t" text-anchor="{anchor}">{E(t)}</text>')

    band(10, 92, "중앙 Server", "메타팩토리|D-1-1 · D-2-1", "ly1")
    boxes(26, [("Enterprise AAS", "Repository"), ("Manufacturing", "Data Lake"), ("Central Historical", "TSDB"),
               ("Enterprise AI", "Feature Store"), ("AI Model", "Registry")], cyl=True, h=62)
    arr(330, 152, 330, 104, "AI Ready 데이터·AAS 서브모델 (MQTT/REST)", "d", "end", -10)
    arr(370, 104, 370, 152, "모델 배포·작업지시", "c")

    band(154, 222, "Local Server", "존별 OCS Cell 코어|각 존 서버실|K8s HA + GPU|+ Scale-out 스토리지", "ly2")
    boxes(170, [("AAS Repository", "Registry"), ("Operational TSDB", "운영 시계열"), ("Data Lake", "Raw · AI Ready 버킷"),
                ("추론용 AI", "Feature Store"), ("AI Inference", "Engine (GPU)")], cyl=True, h=70)
    boxes(256, [("AI Ready 변환 파이프라인", "동기화·정제·AAS 매핑·품질검증"), ("존 오케스트레이터 (OCS)", "Manufacturing·Field Logistics Agent"),
                ("디지털트윈", "공정 검증 DT · 학습 DT"), ("카탈로그·모니터링", "공통 ID·리니지·알람")], h=56)
    o.append('<text x="160" y="352" class="lys2">원시데이터 → 정제·동기화 → AI Ready 변환 → 중앙 전송 · DT는 TSDB·Data Lake를 읽어 리플레이·가상검증</text>')
    arr(330, 430, 330, 378, "OPC UA 통신 (Client/Server · PubSub)", "d", "start", 10)
    arr(700, 430, 700, 378, "대용량 원시데이터 업로드 (S3)", "d", "start", 10)
    arr(560, 378, 560, 430, "엣지 모델·GW 설정 배포", "c")

    band(432, 160, "Edge Gateway", "셀별 EGW +|영상 수집 노드|셀 캐비닛", "ly3")
    o.append('<text x="300" y="454" class="mod-t">OPC UA 모듈</text><text x="560" y="454" class="mod-t">TSDB 모듈</text><text x="770" y="454" class="mod-t">Control 모듈</text>')
    for i, t in enumerate(["AAS 기반 OPC UA 정보모델", "OPC UA Aggregation Server (수집·정규화·AAS 매핑)", "필드장비 인터페이스 (OPC UA Client·드라이버)"]):
        o.append(f'<rect x="150" y="{464 + i * 38}" width="300" height="32" rx="4" class="box"/><text x="300" y="{485 + i * 38}" class="boxt" font-size="11.5">{E(t)}</text>')
    o.append('<path d="M480,474 v74 a80,9 0 0 0 160,0 v-74 a80,9 0 0 0 -160,0 a80,9 0 0 0 160,0" class="box cyl"/>')
    o.append('<text x="560" y="510" class="boxt">시계열 DB · 영상 버퍼</text><text x="560" y="528" class="boxs">시계열(EGW) · 영상(영상 노드)</text>')
    for i, t in enumerate([("AAS 기반 GW 설정", "Gateway 관리·OTA"), ("웹 기반 클라우드 IF", "엣지 AI 모델")]):
        for j, tt in enumerate(t):
            o.append(f'<rect x="{670 + j * 112}" y="{466 + i * 56}" width="104" height="48" rx="4" class="box"/><text x="{722 + j * 112}" y="{494 + i * 56}" class="boxt" font-size="11">{E(tt)}</text>')
    arr(300, 676, 300, 602, "")
    arr(560, 676, 560, 602, "")
    arr(800, 602, 800, 676, "", "c")
    for x_, t_ in [(310, "OPC UA Server (PLC·로봇)"), (570, "Vision·Vibration·Audio 원시데이터"), (810, "레시피·모델·설정")]:
        o.append(f'<text x="{x_}" y="618" class="fl-t">{E(t_)}</text>')

    o.append('<rect x="0" y="626" width="900" height="34" rx="17" class="net"/><text x="450" y="648" class="net-t">Network — Fieldbus(EtherCAT) · OPC UA · TSN(802.1AS 시간동기) · PoE · Wi-Fi 6E/5G</text>')
    o.append('<rect x="0" y="678" width="900" height="114" rx="6" class="ly ly4"/><text x="14" y="706" class="lyt">Field</text><text x="14" y="726" class="lys">실증 존별 셀</text>')
    o.append('<rect x="-6" y="671" width="912" height="128" rx="10" class="fld"/>')
    o.append('<text x="906" y="815" class="fldtag" text-anchor="end">현장 — 실증 존별 셀 (모든 존)</text>')
    zones = ["유연제조 존", "적응가공 존", "정밀조립 존", "AI정밀검사 존", "이기종 물류 존"]
    for i, zn in enumerate(zones):
        x = 150 + i * 150
        ex = zn == "정밀조립 존"
        o.append(f'<rect x="{x}" y="692" width="140" height="86" rx="5" class="box"/>')
        if ex:
            o.append(f'<rect x="{x - 3}" y="689" width="146" height="92" rx="7" class="exhl"/>')
            o.append(f'<text x="{x + 70}" y="815" class="extag" text-anchor="middle">▲ 이 페이지의 예시</text>')
        o.append(f'<text x="{x + 70}" y="711" class="boxt" font-weight="700">{zn}</text>')
        for j, t in enumerate(["PLC · FieldBus · AAS", "로봇·AMR + 온디바이스 엣지", "카메라 · F/T · 센서"]):
            o.append(f'<text x="{x + 70}" y="{730 + j * 16}" class="boxs">{E(t)}</text>')
    # scope
    o.append('<rect x="-6" y="147" width="912" height="452" rx="10" class="own"/>')
    o.append('<text x="906" y="140" class="owntag" text-anchor="end">존별 OCS Cell 범위 — 모든 실증 존 공통</text>')
    # verification column
    o.append('<rect x="930" y="154" width="190" height="438" rx="6" class="ly ly1"/><text x="1025" y="182" class="lyt" text-anchor="middle">검증 영역 (TTA)</text>')
    for i, t in enumerate(["인터페이스·정보모델", "의미매핑·명령/이벤트", "상태전이·시간/순서", "Expected ↔ Actual Trace",
                           "AAS 매핑·Submodel", "Semantic ID·단위/코드", "완전성·결측/이상치", "시간정합성·추적성"]):
        o.append(f'<rect x="944" y="{198 + i * 47}" width="162" height="38" rx="4" class="box"/><text x="1025" y="{222 + i * 47}" class="boxt" font-size="11.5">{E(t)}</text>')
    o.append('<line x1="898" y1="240" x2="928" y2="240" class="fl-d" marker-end="url(#m1)"/><text x="913" y="232" class="fl-t" text-anchor="middle" font-size="10">Trace</text>')
    o.append('<line x1="898" y1="500" x2="928" y2="500" class="fl-d" marker-end="url(#m1)"/><text x="913" y="492" class="fl-t" text-anchor="middle" font-size="10">데이터</text>')
    o.append('<line x1="928" y1="540" x2="898" y2="540" class="fl-c" marker-end="url(#m2)"/><text x="913" y="558" class="fl-t" text-anchor="middle" font-size="10">결과</text>')
    o.append("</g></svg>")
    return "".join(o)


# ------------------------------------------------------------------ 물리 연결 토폴로지
NODE_RULES = [("FW-", "FW"), ("CORE-", "CORE"), ("LS-", "LS"), ("GPU-", "GPU"), ("KVM", "KVM"), ("STO-", "STO"),
              ("BAK", "BAK"), ("PTP", "PTP"), ("MGT", "MGT"), ("UPS", "UPS"), ("OWS", "OWS"), ("DWS", "DWS"),
              ("비디오월", "VW"), ("EGW", "EGW"), ("영상 노드", "VNODE"), ("로봇 CTRL", "c:EDGE-T"), ("AMR·모바일", "c:EDGE-O"), ("TSN SW", "TSN"), ("액세스·PoE", "POE"), ("AP", "AP")]


def node_sym(t):
    for pre, sym in NODE_RULES:
        if t.startswith(pre):
            return sym
    return None


SW_NODE = {
    "OPCUA": ("EGW", "Edge Gateway"), "AASIM": ("EGW", "Edge Gateway"), "DRV": ("EGW", "Edge Gateway"),
    "ETSDB": ("EGW", "Edge Gateway"), "RAW": ("VNODE", "영상 수집 노드"), "GWM": ("EGW", "Edge Gateway (관리 콘솔은 로컬 서버)"),
    "EAI": ("VNODE", "영상 수집 노드 (F/T 모델은 EGW)"), "K8S": ("LS", "로컬 서버 LS-1~3"), "AASR": ("LS", "로컬 서버 LS-1~3"),
    "OTSDB": ("LS", "로컬 서버 LS-1~3"), "LAKE": ("STO", "스토리지 STO-1~9"), "FS": ("LS", "로컬 서버 LS-1~3"),
    "INF": ("GPU", "GPU 서버 GPU-1"), "ETL": ("LS", "로컬 서버 (GPU-2 연산 사용)"), "MQTT": ("LS", "로컬 서버 LS-1~3"),
    "CAT": ("LS", "로컬 서버 LS-1~3"), "OCS": ("LS", "로컬 서버 (관제는 OWS)"), "DMW": ("DWS", "DT 워크스테이션"),
    "ISAAC": ("DWS", "DT 워크스테이션 (GPU 서버 병행)"), "MON": ("LS", "로컬 서버 LS-1~3"), "SEC": ("LS", "로컬 서버 + 방화벽"),
    "TRC": ("LS", "로컬 서버 LS-1~3"),
}


def topo_svg():
    o = ['<svg class="arch plan" viewBox="0 0 1120 1012" role="img" aria-label="정밀조립존 OCS Cell 물리 연결 토폴로지" style="max-width:1120px">']

    used = set()

    def dev(x, y, w, h, t, s="", cls="dv", fs=12):
        sym = node_sym(t)
        if sym:
            pre = "hw"
            if sym.startswith("c:"):
                pre, sym = "chw", sym[2:]
            nid = f' id="topo-{sym}"' if sym not in used else ""
            used.add(sym)
            label = "셀 HW" if pre == "chw" else "존 HW"
            o.append(f'<a href="#{pre}-{sym}" class="nlink" aria-label="{E(t)} — {label} {sym} 항목으로 이동"><g data-node="{sym}"{nid}>')
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" class="{cls}"/>')
        o.append(f'<text x="{x + w / 2}" y="{y + (h / 2 + 4 if not s else h / 2 - 2)}" class="dvt" font-size="{fs}">{E(t)}</text>')
        if s:
            o.append(f'<text x="{x + w / 2}" y="{y + h / 2 + 13}" class="dvs">{E(s)}</text>')
        if sym:
            o.append('</g></a>')

    def tlink(sym, svg):
        nid = f' id="topo-{sym}"' if sym not in used else ""
        used.add(sym)
        return f'<a href="#hw-{sym}" class="nlink"><g data-node="{sym}"{nid}>{svg}</g></a>'

    def link(pts, cls, label="", lx=None, ly=None, anchor="start"):
        d = " ".join(f"{x},{y}" for x, y in pts)
        o.append(f'<polyline points="{d}" class="lk {cls}"/>')
        if label:
            o.append(f'<text x="{lx}" y="{ly}" class="lkt" text-anchor="{anchor}">{E(label)}</text>')

    # external
    dev(330, 14, 300, 54, "중앙 Server (메타팩토리 DCC · AAS 통합서버)", "산학융합플라자 · D-1-1 / D-2-1", "ext")
    dev(800, 14, 250, 54, "TTA 검증 영역 (원격)", "Trace · 데이터/메타데이터", "ext")
    # firewall
    dev(380, 136, 90, 40, "FW-1", "", "dv2")
    dev(490, 136, 90, 40, "FW-2", "", "dv2")
    link([(430, 68), (430, 136)], "l10", "캠퍼스 광 10G×2 · AI Ready 전송 MQTT/REST(TLS)", 438, 95)
    link([(530, 68), (530, 136)], "l10")
    link([(925, 68), (925, 156), (580, 156)], "l10", "검증 API (VPN)", 792, 150)
    # 정밀조립존 영역 (서버실·관제실·A-3-1~5)
    o.append('<rect x="8" y="78" width="1104" height="926" rx="12" class="zonebd"/><text x="22" y="94" class="zonebd-t">정밀조립존 (A-3)</text>')
    # server room
    o.append('<rect x="20" y="100" width="760" height="386" rx="8" class="room"/><text x="34" y="122" class="room-t">존 서버실 (28.8㎡) — 방화벽 · Rack A 연산 · Rack B 스토리지·네트워크</text>')
    dev(330, 226, 120, 44, "CORE-1", "L3 25/100G", "dv2")
    dev(470, 226, 120, 44, "CORE-2", "MLAG", "dv2")
    link([(410, 176), (380, 226)], "l10a")
    link([(450, 176), (500, 226)], "l10b")
    link([(510, 176), (420, 226)], "l10a")
    link([(560, 176), (550, 226)], "l10b")
    link([(450, 248), (470, 248)], "l100")
    # rack A
    o.append('<rect x="40" y="290" width="330" height="180" rx="5" class="rack"/>' + tlink("RACK", '<text x="52" y="308" class="rack-t">Rack A · 연산</text>'))
    for i in range(3):
        dev(52 + i * 104, 318, 96, 46, f"LS-{i + 1}", "로컬 서버 노드")
    dev(52, 376, 200, 46, "GPU-1", "실시간 추론 (RTX PRO 6000×4)")
    dev(262, 376, 96, 46, "GPU-2", "배치·비식별·합성")
    dev(52, 430, 96, 32, "KVM", "", "dv3", 11)
    # rack B
    o.append('<rect x="400" y="290" width="370" height="180" rx="5" class="rack"/>' + tlink("RACK", '<text x="412" y="308" class="rack-t">Rack B · 스토리지·네트워크 (Rack C 별도)</text>'))
    for i in range(4):
        dev(412 + i * 88, 318, 80, 46, f"STO-{i + 1}", "raw·ai-ready")
    for i in range(3):
        dev(412 + i * 88, 376, 80, 46, f"STO-{i + 5}" if i < 2 else f"STO-7~{N_STO}", "raw·ai-ready")
    dev(676, 376, 84, 46, "BAK", "백업 NAS", "dv3")
    dev(412, 430, 100, 32, "PTP GM", "", "dv3", 11)
    dev(520, 430, 100, 32, "MGT SW", "", "dv3", 11)
    dev(628, 430, 132, 32, "UPS 20kVA · CRAC", "", "dv3", 11)
    link([(345, 270), (345, 280), (200, 280), (200, 290)], "l25a")
    link([(485, 270), (485, 285), (214, 285), (214, 290)], "l25b")
    o.append('<text x="120" y="282" class="lkt">25GbE×2/노드 (코어별 1)</text>')
    link([(430, 270), (430, 279), (580, 279), (580, 290)], "l25a")
    link([(570, 270), (570, 284), (594, 284), (594, 290)], "l25b")
    o.append('<text x="604" y="283" class="lkt">25GbE×4/노드 (코어별 2)</text>')
    link([(412, 446), (385, 446), (385, 262), (330, 262)], "ptp")
    # control room
    o.append('<rect x="800" y="186" width="300" height="300" rx="8" class="room"/><text x="814" y="208" class="room-t">로컬존 DCC 관제실</text>')
    dev(820, 230, 125, 50, "OWS×2", "OCS 운영")
    dev(960, 230, 125, 50, "DWS×2", "DT·시뮬레이션")
    dev(820, 300, 265, 60, "비디오월 55″ 2×2", "셀 영상·DT·KPI")
    dev(820, 380, 265, 80, "운영자 HMI 데스크", "알람 대응 · HOLD/재배정 승인", "dv3")
    link([(590, 252), (800, 252)], "l10b", "10GbE×2", 690, 246)
    link([(440, 226), (440, 210), (800, 210)], "l10a")
    # 통로 AP 2대 (AMR 주통로 천장, 셀 간 이동 중 로밍)
    for ax in (110, 560):
        dev(ax, 500, 120, 40, "AP (통로)", "Wi-Fi 6E · 통로 천장", "dv2", 11)
        o.append(f'<path d="M{ax + 124},{520} q4,-6 8,0 q4,6 8,0 q4,-6 8,0 q4,6 8,0" class="lk wl"/>')
        o.append(f'<text x="{ax + 160}" y="{524}" class="lkt">셀 간 이동 AMR</text>')
        link([(ax + 60, 540), (ax + 60, 556)], "poe")
    o.append('<g transform="translate(0,44)">')
    # cable tray
    o.append(tlink("FIB", '<rect x="20" y="512" width="1080" height="16" rx="3" class="tray"/><text x="560" y="524" class="tray-t" text-anchor="middle">존 통로 상부 케이블 트레이 — 셀 액세스 스위치 ↔ 서버실 10GbE 이중 광(OM4) · PTP(802.1AS)</text>'))
    link([(377, 270), (377, 556)], "l25a")
    link([(520, 270), (520, 288), (391, 288), (391, 556)], "l25b")
    # cells
    cells = [(cid, "TSN×4 · PoE×2", True) for cid in ("A-3-5", "A-3-2", "A-3-3", "A-3-1", "A-3-4")]
    for i, (cid, yr, now) in enumerate(cells):
        x = 20 + i * 218
        cls = "cab" if now else "cab later"
        o.append(f'<rect x="{x}" y="556" width="208" height="330" rx="6" class="{cls}"/>')
        o.append(tlink("CAB", f'<text x="{x + 10}" y="576" class="cab-t">{cid} 셀 캐비닛 · {yr}</text>'))
        link([(x + 96, 528), (x + 96, 586)], "l25a")
        link([(x + 112, 528), (x + 112, 586)], "l25b")
        dev(x + 14, 586, 86, 40, "EGW", "OPC UA·AAS", "dv" if now else "dvx", 11)
        dev(x + 108, 586, 86, 40, "영상 노드", f"L4·{BUF_D}일 버퍼", "dv" if now else "dvx", 11)
        dev(x + 14, 638, 86, 36, "TSN SW", "", "dv2" if now else "dvx", 11)
        dev(x + 108, 638, 86, 36, "액세스·PoE", "", "dv2" if now else "dvx", 11)
        link([(x + 57, 626), (x + 57, 638)], "l10")
        link([(x + 151, 626), (x + 151, 638)], "l10")
        # field devices
        dev(x + 10, 712, 90, 44, "셀 PLC", "안전PLC·AAS", "fd", 11)
        dev(x + 108, 712, 90, 44, "공정 비전", "검사 카메라 PoE", "fd", 11)
        dev(x + 10, 824, 90, 44, "로봇 CTRL", "+ 엣지 · D405/D455", "fd", 11)
        dev(x + 108, 768, 90, 44, "F/T·센서", "1kHz", "fd", 11)
        dev(x + 10, 768, 90, 44, "서보·설비", "EtherCAT", "fd", 11)
        dev(x + 108, 824, 90, 44, "AMR·모바일", "Wi-Fi 6E + 5G 모뎀", "fd", 11)
        link([(x + 40, 674), (x + 40, 712)], "l1")
        link([(x + 151, 674), (x + 151, 712)], "poe")
        link([(x + 80, 674), (x + 80, 690), (x + 104, 690), (x + 104, 846), (x + 100, 846)], "l1")
        link([(x + 55, 756), (x + 55, 768)], "fb")
        link([(x + 30, 812), (x + 30, 824)], "fb")
        link([(x + 194, 656), (x + 202, 656), (x + 202, 790), (x + 198, 790)], "l1")
        # 무선: AMR·모바일 → 셀 천장 AP (AP는 PoE로 셀 액세스 스위치에 연결)
        dev(x + 108, 904, 90, 40, "AP", "Wi-Fi 6E · 셀 천장", "dv2", 11)
        o.append(f'<path d="M{x + 153},{868} q-6,4 0,9 q6,4 0,9 q-6,4 0,9 q6,4 0,8" class="lk wl"/>')
        link([(x + 198, 924), (x + 213, 924), (x + 213, 664), (x + 194, 664)], "poe")
    o.append("</g>")
    o.append("</svg>")
    return "".join(o)


LEGEND_TOPO = [("l100", "100GbE (코어 간 MLAG 피어링)"), ("l25a", "CORE-1 측 연결 (25GbE 서버 / 10GbE 셀 업링크)"), ("l25b", "CORE-2 측 연결 (이중화 짝)"), ("l10a", "10GbE · CORE-1 측"), ("l10b", "10GbE · CORE-2 측"), ("l1", "1/10GbE 산업 Ethernet (OPC UA)"),
               ("poe", "PoE+ 2.5GbE (카메라·AP)"), ("fb", "Fieldbus EtherCAT (실시간 제어)"), ("ptp", "PTP 시간동기"), ("wl", "무선 Wi-Fi 6E (AMR·AMMR ↔ AP) · 5G는 로봇 모뎀 → 이음5G(별도)")]


# ------------------------------------------------------------------ 설치 배치도 (존 평면)
def floor_svg():
    U = 100
    W, H = ZONE["W"] * U, ZONE["H"] * U
    m = 200
    o = [f'<svg class="plan zone" viewBox="{-m} {-m - 100} {W + 2 * m} {H + 2 * m + 100}" role="img" aria-label="OCS Cell 설치 배치도">']
    o.append(f'<rect x="0" y="0" width="{W}" height="{H}" class="bldg"/>')
    o.append(f'<rect x="50" y="1320" width="{W - 100}" height="320" class="aisle"/>')
    for b in ZONE["blocks"]:
        x, y, w, h, kind, title, sub = b
        X, Y, Wd, Hd = x * U, y * U, w * U, h * U
        hl = " hl" if title in ("로컬 DCC 관제실", "엣지 서버·네트워크실") else ""
        o.append(f'<rect x="{X}" y="{Y}" width="{Wd}" height="{Hd}" class="blk {kind}{hl}"/>')
        fs = 100 if kind == "cell" else min(64, (Wd - 30) / (len(title) * 0.95))
        ty = Y + 90 if hl else Y + Hd / 2
        shown = "로컬존 DCC 관제실" if title == "로컬 DCC 관제실" else title
        o.append(f'<text x="{X + Wd / 2}" y="{ty}" class="blk-t {kind}" font-size="{(46 if hl else fs):.0f}">{E(shown)}</text>')
    # cable tray along aisle (top edge) + riser to server room
    tray_y = 1360
    o.append(f'<line x1="150" y1="{tray_y}" x2="{38.0 * U}" y2="{tray_y}" class="tray-l"/>')
    o.append(f'<polyline points="{34.0 * U},{tray_y} {34.0 * U},{2640} {34.9 * U},{2640}" class="tray-l"/>')
    o.append(f'<text x="900" y="{tray_y + 80}" class="flr-t">케이블 트레이 (통로 상부, 광 10G 이중·Cat6A·PTP)</text>')
    # cabinets: near aisle side of each cell
    cabs = {"A-3-5": (1250, 1250), "A-3-4": (3050, 1250), "A-3-2": (3750, 1230), "A-3-3": (850, 1650), "A-3-1": (2150, 1650)}
    later = {"A-3-5": False}
    for cid, (cx, cy) in cabs.items():
        cls = "cabf"
        o.append(f'<rect x="{cx - 60}" y="{cy - 50}" width="120" height="100" class="{cls}"/>')
        o.append(f'<text x="{cx}" y="{cy + 14}" class="cabf-t">CAB</text>')
        o.append(f'<line x1="{cx}" y1="{cy + (50 if cy < 1400 else -50)}" x2="{cx}" y2="{tray_y}" class="drop"/>')
    # AP positions
    for ax, ay in ((850, 880), (2550, 880), (3850, 880), (615, 2460), (1845, 2460), (1500, 1560), (3000, 1560)):
        o.append(f'<circle cx="{ax}" cy="{ay}" r="34" class="apf"/><text x="{ax}" y="{ay + 12}" class="apf-t">AP</text>')
    # server room racks — 엣지 서버·네트워크실(x 3450~4050, y 2430~2910) 가운데 정렬
    o.append('<rect x="3510" y="2580" width="160" height="120" class="rackf"/><rect x="3700" y="2580" width="160" height="120" class="rackf"/>')
    o.append('<text x="3590" y="2655" class="cabf-t">A</text><text x="3780" y="2655" class="cabf-t">B</text>')
    o.append('<rect x="3890" y="2580" width="100" height="120" class="rackf2"/><text x="3940" y="2655" class="cabf-t" font-size="34">UPS</text>')
    o.append('<rect x="3650" y="2750" width="200" height="90" class="rackf2"/><text x="3750" y="2808" class="cabf-t" font-size="34">CRAC</text>')
    # control room — 로컬존 DCC 관제실(x 3450~4050, y 1640~2380) 가운데 정렬
    o.append('<rect x="3540" y="1840" width="420" height="40" class="vwf"/><text x="3750" y="1940" class="flr-s">비디오월</text>')
    for i in range(4):
        o.append(f'<rect x="{3510 + i * 125}" y="2010" width="105" height="70" class="deskf"/>')
    o.append('<text x="3750" y="2150" class="flr-s">OWS×2 · DWS×2</text>')
    o.append(f'<line x1="0" y1="-110" x2="{W}" y2="-110" class="dim"/><text x="{W / 2}" y="-140" class="dim-t z">46.0 m</text>')
    o.append('<text x="0" y="-150" class="zone-ttl">정밀조립존 (A-3)</text>')
    o.append("</svg>")
    return "".join(o)


EXTRA = """<style>
:root{--field:#2E9E5E}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--field:#4CC27E}}
:root[data-theme="dark"]{--field:#4CC27E}
.arch text{font-family:var(--font)}
.ly{stroke:none} .ly1{fill:var(--navy)} .ly2{fill:var(--navy2)} .ly3{fill:#2E5AA8} .ly4{fill:#5E86C8}
.lyt{fill:#fff;font-size:15px;font-weight:700} .lys{fill:#C9D6F0;font-size:11px} .lys2{fill:#DCE6F8;font-size:11px}
.box{fill:var(--paper)} .cyl{stroke:var(--eqline);stroke-width:1}
.boxt{fill:var(--ink);font-size:12.5px;text-anchor:middle} .boxs{fill:var(--muted);font-size:10.5px;text-anchor:middle}
.mod-t{fill:#fff;font-size:13px;font-weight:700;text-anchor:middle}
.own{fill:none;stroke:var(--amber);stroke-width:3}
.exhl{fill:var(--teal);fill-opacity:.12;stroke:var(--teal);stroke-width:3} .extag{fill:var(--teal);font-size:12px;font-weight:700}
.owntag{fill:var(--amber);font-size:12px;font-weight:700}
.sfh{fill:var(--teal);font-size:13px;font-weight:700} .sflane{fill:var(--area)} .sflt{fill:var(--muted);font-size:11.5px;font-weight:700}
.sfres{fill:var(--navy2);stroke:var(--amber);stroke-width:2} .sft-w{fill:#fff;text-anchor:middle;font-weight:700} .sfs-w{fill:#C9D6F0;font-size:10.5px;text-anchor:middle}
.sfn{fill:var(--muted);font-size:12px}
.mast p{max-width:none}
.zone-ttl{fill:var(--navy2);font-size:86px;font-weight:900}
.fld{fill:none;stroke:var(--field);stroke-width:3} .fldtag{fill:var(--field);font-size:12px;font-weight:700}
.fl-d{stroke:var(--cyan);stroke-width:2.4;fill:none} .fl-c{stroke:#9DB8E8;stroke-width:2.4;fill:none;stroke-dasharray:6 4}
.fl-t{font-size:11px;fill:var(--ink);paint-order:stroke;stroke:var(--bg);stroke-width:4px}
.net{fill:var(--teal)} .net-t{fill:#fff;font-size:13px;font-weight:700;text-anchor:middle}
.ext{fill:var(--navy);} .ext + text,.ext ~ text{}
.dv{fill:var(--paper);stroke:var(--navy2);stroke-width:1.6} .dv2{fill:var(--grp);stroke:var(--navy2);stroke-width:1.6}
.dv3{fill:var(--area);stroke:var(--eqline);stroke-width:1} .dvx{fill:var(--paper);stroke:var(--muted);stroke-width:1.2;stroke-dasharray:4 3}
.fd{fill:var(--cellbg);stroke:var(--eqline);stroke-width:1}
.dvt{fill:var(--ink);text-anchor:middle;font-weight:700} .dvs{fill:var(--muted);font-size:10px;text-anchor:middle}
rect.ext + text{fill:#fff}
.zonebd{fill:none;stroke:var(--navy2);stroke-width:2.2;stroke-dasharray:14 7} .zonebd-t{fill:var(--navy2);font-size:13px;font-weight:700}
.room{fill:none;stroke:var(--eqline);stroke-width:1.5;stroke-dasharray:8 5} .room-t{fill:var(--teal);font-size:12.5px;font-weight:700}
.rack{fill:var(--cellbg);stroke:var(--ink);stroke-width:1.5} .rack-t{fill:var(--muted);font-size:11.5px;font-weight:700}
.tray{fill:var(--aisle);stroke:var(--teal);stroke-width:1} .tray-t{fill:var(--teal);font-size:11px;font-weight:700}
.cab{fill:none;stroke:var(--navy2);stroke-width:2} .cab.later{stroke:var(--muted);stroke-dasharray:6 4}
.cab-t{fill:var(--ink);font-size:12px;font-weight:700}
.lk{fill:none} .l100{stroke:var(--navy);stroke-width:5} .l25{stroke:var(--teal);stroke-width:3.4} .l10{stroke:var(--navy2);stroke-width:2.2}
.l25a{stroke:var(--teal);stroke-width:3} .l25b{stroke:var(--teal);stroke-width:3;stroke-dasharray:7 4}
.l10a{stroke:var(--navy2);stroke-width:2} .l10b{stroke:var(--navy2);stroke-width:2;stroke-dasharray:6 4}
.l1{stroke:var(--eqline);stroke-width:1.6} .poe{stroke:var(--amber);stroke-width:2} .fb{stroke:var(--hum);stroke-width:2.6}
.ptp{stroke:var(--cyan);stroke-width:1.6;stroke-dasharray:3 3} .wl{stroke:var(--amr);stroke-width:2}
.lkt{font-size:10.5px;fill:var(--ink);paint-order:stroke;stroke:var(--bg);stroke-width:4px}
.lg{display:flex;flex-wrap:wrap;gap:6px 16px;list-style:none;padding:0;margin:10px 0 0;font-size:12.5px;color:var(--muted)}
.lg svg{vertical-align:middle;margin-right:4px}
.blk.hl{stroke:var(--amber);stroke-width:22}
.tray-l{stroke:var(--teal);stroke-width:26;stroke-linecap:round;opacity:.75;fill:none}
.drop{stroke:var(--teal);stroke-width:10;stroke-dasharray:24 14}
.cabf{fill:var(--navy2)} .cabf.later{fill:var(--muted)} .cabf-t{fill:#fff;font-size:40px;font-weight:700;text-anchor:middle}
.apf{fill:var(--amr)} .apf-t{fill:#fff;font-size:30px;font-weight:700;text-anchor:middle}
.rackf{fill:var(--navy)} .rackf2{fill:var(--navy2)} .vwf{fill:var(--ink)} .deskf{fill:var(--paper);stroke:var(--ink);stroke-width:6}
.flr-t{fill:var(--teal);font-size:56px;font-weight:700} .flr-s{fill:var(--ink);font-size:44px;text-anchor:middle}
td.q{text-align:center;font-family:var(--mono);font-variant-numeric:tabular-nums}
td.q.z{color:var(--muted)}
table.issuetbl th[scope=row]{white-space:nowrap;color:var(--navy2);font-weight:700;background:var(--grp)}
table.issuetbl td{font-size:13px;line-height:1.55}
table.issuetbl td:nth-child(3){min-width:320px}
table.sumtbl th{width:130px;background:var(--grp);color:var(--navy2);font-weight:700;white-space:nowrap;vertical-align:top}
table.sumtbl td{font-size:13.5px;line-height:1.6}
.nlink{cursor:pointer}
.nlink:hover rect,.nlink:focus rect{stroke:var(--amber)!important;stroke-width:3!important}
.nlink:hover text.rack-t,.nlink:hover text.cab-t,.nlink:hover text.tray-t{fill:var(--amber)}
g.flash rect{stroke:var(--amber)!important;stroke-width:4!important}
g.flash text{fill:var(--amber)}
tr.flash td{background:color-mix(in srgb, var(--amber) 22%, var(--paper))!important;transition:background .3s}
a.tolink{color:var(--teal);text-decoration:none;font-weight:700}
a.tolink:hover,a.tolink:focus-visible{text-decoration:underline}
a.tolink:not(.sw){font-size:11px;font-weight:500;margin-left:4px;white-space:nowrap}
span.where{display:block;font-size:11px;font-weight:400;color:var(--muted);margin-top:2px}
td.prod{min-width:200px;font-weight:500;color:var(--navy2)}
td.mk{min-width:120px;font-size:12px}
td.basis{min-width:220px;font-size:12px}
td.uc{min-width:320px;font-size:12.5px;color:var(--ink);background:color-mix(in srgb, var(--cyan) 6%, transparent)}
td.src{min-width:120px;font-size:12px;white-space:nowrap}
td.src a{color:var(--teal)}
table.wide{min-width:1900px}
</style>"""


def legend_topo():
    out = []
    for cls, t in LEGEND_TOPO:
        out.append(f'<li><svg width="34" height="10" aria-hidden="true"><line x1="0" y1="5" x2="34" y2="5" class="lk {cls}"/></svg>{E(t)}</li>')
    return '<ul class="lg">' + "".join(out) + "</ul>"


def k(n):  # 만원 → 천원 표시
    return bp.fmt(n * 10)


def cost(sym, q):
    return P[sym][2] * q


def total(rows):
    return sum(cost(r[1], r[4] + r[5] + r[6]) for r in rows)


def links(sym):
    ls = SRC.get(sym, [])
    if not ls:
        return ""
    return "<br>".join(f'<a href="{E(u)}" target="_blank" rel="noopener">{E(t)} ↗</a>' for t, u in ls)


TOPO_SYMS = {"FW", "CORE", "LS", "GPU", "KVM", "STO", "BAK", "PTP", "MGT", "UPS", "OWS", "DWS", "VW", "EGW", "VNODE", "TSN", "POE", "AP", "RACK", "FIB", "CAB"}


# HW → 탑재 SW (SW 목록 순서 유지)
HW_SW = {}
for _r in SW:
    _node = SW_NODE.get(_r[1], (None,))[0]
    if _node:
        HW_SW.setdefault(_node, []).append(_r[1])
for _hw, _extra in (("GPU", ["ETL", "ISAAC"]), ("OWS", ["OCS"]), ("FW", ["SEC"])):
    for _x in _extra:
        if _x not in HW_SW.setdefault(_hw, []):
            HW_SW[_hw].append(_x)


def item_table(rows, with_loc=True):
    head = ("<tr><th>기호</th><th>품목</th><th>주요 스펙</th><th>추천 제품·모델</th><th>제조사 (국가)</th>"
            "<th>수량</th><th>단위</th><th>단가</th><th>금액</th><th>용도</th>" + ("<th>설치 위치</th>" if with_loc else "")
            + ("" if with_loc else "<th>Use Case (정밀조립존 적용 예)</th>") + "<th>수량 근거</th><th>가격 근거</th><th>사양·가격 출처</th></tr>")
    ncol = 14
    body, cur, gsum = [], None, {}
    for r in rows:
        gsum[r[0]] = gsum.get(r[0], 0) + cost(r[1], r[4] + r[5] + r[6])
    for r in rows:
        if with_loc:
            g, sym, name, spec, q1, q2, q3, unit, use, loc = r
        else:
            g, sym, name, spec, q1, q2, q3, unit, use = r
            loc = None
        q = q1 + q2 + q3
        if g != cur:
            cur = g
            body.append(f'<tr class="grp"><th colspan="8" scope="rowgroup">{E(g)}</th><td class="num">{k(gsum[g])}</td><td colspan="{ncol - 9}"></td></tr>')
        prod, maker, up, basis_price = P[sym]
        rid = f'{"hw" if with_loc else "sw"}-{sym}'
        if with_loc:
            tsym = {"CRAC": "UPS"}.get(sym, sym)
            sws = HW_SW.get(sym, [])
            if sws:
                ids = ",".join("sw-" + x for x in sws)
                names = " · ".join(P[x][0].split(" (")[0] for x in sws[:3]) + (f" 외 {len(sws) - 3}" if len(sws) > 3 else "")
                nm = (f'<a href="#sw-{sws[0]}" class="tolink sw" data-flash="{ids}">{E(name)}</a>'
                      f'<span class="where">탑재 SW {len(sws)}종: {E(names)} ↓</span>')
            else:
                nm = E(name)
            nm += (f' <a href="#topo-{tsym}" class="tolink">도면 ↑</a>' if tsym in TOPO_SYMS else "")
        else:
            node, nlabel = SW_NODE.get(sym, (None, ""))
            nm = (f'<a href="#topo-{node}" class="tolink sw">{E(name)}</a><span class="where">설치: {E(nlabel)} ↑</span>' if node else E(name))
        body.append(f'<tr id="{rid}"><td class="sym">{E(sym)}</td><td class="nm">{nm}</td><td class="spec">{E(spec)}</td>'
                    f'<td class="prod">{E(prod)}</td><td class="mk">{E(maker)}</td><td class="q"><b>{q}</b></td><td class="u">{E(unit)}</td>'
                    f'<td class="num">{k(up) if up else "0"}</td><td class="num">{k(up * q)}</td><td>{E(use)}</td>'
                    + (f'<td class="note">{E(loc)}</td>' if with_loc else f'<td class="uc">{E(USE.get(sym, ""))}</td>')
                    + f'<td class="basis">{E(BASIS[sym])}</td><td class="note">{E(basis_price)}</td><td class="src">{links(sym)}</td></tr>')
    t = total(rows)
    foot = f'<tr class="tot strong"><th colspan="8">합계</th><td class="num" colspan="2">{k(t)} 천원</td><td colspan="{ncol - 10}"></td></tr>'
    return f'<div class="tbl-wrap"><table class="bom wide"><thead>{head}</thead><tbody>{"".join(body)}</tbody><tfoot>{foot}</tfoot></table></div>'


def size_flow_svg():
    """② 셀별 발생량 풀이 도식 — 장치 1대 → 대수 곱 → 셀 대역폭 → 월 발생량"""
    cnt = dict(ROBOTS)
    tel_cell = sum(n * TEL_BPS[name] for name, n in ROBOTS)          # B/s
    cam_cell = CAM_CELL
    tel_mbps = tel_cell * 8 / 1e6
    cell = cam_cell + tel_mbps
    mbs = cell / 8
    o = ['<svg class="arch plan" viewBox="0 0 1120 500" role="img" aria-label="셀별 원시데이터 발생량 산정 흐름" style="max-width:1120px">',
         '<defs><marker id="sf" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="var(--cyan)"/></marker></defs>']

    def box(x, y, w, h, t, s="", cls="dv", fs=12.5):
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" class="{cls}"/>')
        ty = y + h / 2 + (4 if not s else -3)
        tc = "sft-w" if cls == "sfres" else "dvt"
        sc = "sfs-w" if cls == "sfres" else "dvs"
        o.append(f'<text x="{x + w / 2}" y="{ty}" class="{tc}" font-size="{fs}">{E(t)}</text>')
        if s:
            o.append(f'<text x="{x + w / 2}" y="{y + h / 2 + 13}" class="{sc}">{E(s)}</text>')

    def arr(pts, t="", tx=None, ty=None, anchor="middle"):
        d = " ".join(f"{a},{b}" for a, b in pts)
        o.append(f'<polyline points="{d}" class="fl-d" stroke-width="2" marker-end="url(#sf)"/>')
        if t:
            o.append(f'<text x="{tx}" y="{ty}" class="fl-t" text-anchor="{anchor}" font-weight="700">{E(t)}</text>')

    # 단계 머리
    for x, w, t in [(20, 250, "① 장치 1대 기록 대역폭"), (318, 210, "② 로봇 1대·대수 곱"), (576, 230, "③ 셀 대역폭"), (850, 250, "④ 월 발생량 환산")]:
        o.append(f'<text x="{x}" y="22" class="sfh">{E(t)}</text>')
    # 레인
    o.append('<rect x="10" y="34" width="806" height="212" rx="8" class="sflane"/><text x="22" y="54" class="sflt">카메라 영상 (로봇당 3대 + 협동로봇 엑소센트릭 1대)</text>')
    o.append('<rect x="10" y="258" width="806" height="186" rx="8" class="sflane"/><text x="22" y="278" class="sflt">로봇 텔레메트리 (로봇 종류별)</text>')
    # 카메라 레인: 공통 3대
    for (name, sp, mbps, _), y in zip(CAMS, [62, 104, 146]):
        model = name.split("(")[1].rstrip(")").replace("RealSense ", "")
        box(20, y, 250, 38, f"{name.split(' (')[0]}  {mbps:.1f} Mbps", f"{model} · RGB 4 + Depth {mbps - 4:.1f} (무손실 4:1)")
        arr([(270, y + 19), (296, y + 19), (296, 120), (316, 120)])
    o.append('<text x="306" y="112" class="fl-t" text-anchor="middle" font-weight="700">합</text>')
    box(318, 98, 210, 44, f"로봇 1대 {CAM_MBPS:.1f} Mbps", " + ".join(f"{c[2]:.1f}" for c in CAMS) + f"  × {N_ROBOT}대")
    arr([(528, 120), (552, 120), (552, 166), (574, 166)])
    # 협동로봇 엑소센트릭
    box(20, 196, 250, 40, f"엑소센트릭  {EXO[2]:.1f} Mbps", "D455 · 협동로봇만 · RGB 4 + Depth 18.4")
    arr([(270, 216), (316, 216)], f"× {N_EXO}대", 293, 209)
    box(318, 196, 210, 40, f"{N_EXO * EXO[2]:.0f} Mbps", f"{EXO[2]:.1f} × {N_EXO}")
    arr([(528, 216), (552, 216), (552, 166), (574, 166)])
    box(576, 136, 230, 60, f"셀 카메라 {cam_cell:.0f} Mbps", f"{N_CAM}대 · {CAM_MBPS:.1f}×{N_ROBOT} + {EXO[2]:.1f}×{N_EXO}", "dv2")
    # 텔레메트리 레인
    ty0 = [288, 338, 388]
    for (name, n), y in zip(ROBOTS, ty0):
        bps = TEL_BPS[name]
        sub = {"협동로봇": "관절 7축·TCP 100Hz + F/T 1kHz", "AMR": "LiDAR 2대 + 주행·IMU", "AMMR 양팔로봇": "양팔 14축·F/T 2 + 이동부"}[name]
        box(20, y, 250, 42, f"{name}  {bps / 1000:.0f} KB/s", sub)
        arr([(270, y + 21), (316, y + 21)], f"× {n}대", 293, y + 14)
        box(318, y, 210, 42, f"{n * bps / 1000:,.0f} KB/s", f"{bps / 1000:.0f} × {n}")
        arr([(528, y + 21), (552, y + 21), (552, 351), (574, 351)])
    o.append('<text x="562" y="343" class="fl-t" text-anchor="middle" font-weight="700">합</text>')
    box(576, 322, 230, 58, f"셀 텔레메트리 {tel_mbps:.1f} Mbps", f"{tel_cell / 1000:,.0f} KB/s × 8 ÷ 1,000", "dv2")
    # 합류 → 환산 (위에서 아래로)
    arr([(806, 166), (830, 166), (830, 68), (848, 68)])
    arr([(806, 351), (830, 351), (830, 68), (848, 68)])
    o.append('<text x="838" y="200" class="fl-t" text-anchor="middle" font-weight="700">합</text>')
    box(850, 40, 250, 56, f"셀 평균 {cell:.0f} Mbps", f"영상 {cam_cell:.0f} + 텔레메트리 {tel_mbps:.1f}", "dv2", 14)
    arr([(975, 96), (975, 116)])
    box(850, 118, 250, 44, f"÷ 8 → {mbs:.1f} MB/s", "비트 → 바이트")
    arr([(975, 162), (975, 182)])
    box(850, 184, 250, 56, f"× 3,600초 × {OPS_H}h ÷ 10⁶", f"월 운용 8h × 22일 = {OPS_H}h · MB → TB")
    arr([(975, 240), (975, 266)])
    box(850, 268, 250, 56, f"셀 {SZ[0]['tot']:.1f} TB/월", f"{mbs:.1f} × 3,600 × {OPS_H} ÷ 10⁶", "sfres", 15)
    arr([(975, 324), (975, 356)], "× 5셀", 1000, 345)
    box(850, 358, 250, 56, f"존 {MONTH_TB:.0f} TB/월", f"{SZ[0]['tot']:.1f} × 5셀", "sfres", 15)
    o.append(f'<text x="20" y="480" class="sfn">영상이 셀 발생량의 {cam_cell / cell * 100:.0f}%를 차지함 → 저장 용량은 카메라 수·비트레이트에 가장 민감함. 운용 중 연속 기록 가정(10진 TB).</text>')
    o.append("</svg>")
    return '<figure class="fig" style="margin:10px 0 14px">' + "".join(o) + "</figure>"


def cap_flow_svg():
    """③ 필요 저장 용량 산정 도식 — 존 원시 월 발생량 → 보관 → 여유 → Ceph 사용률 → 노드 수"""
    air_m = MONTH_TB * AIR_RATIO
    keep = RAW_TB + AIR_TB
    usable_need = NEED_TB / FILL
    o = ['<svg class="arch plan" viewBox="0 0 1120 430" role="img" aria-label="필요 저장 용량 산정 흐름" style="max-width:1120px">',
         '<defs><marker id="cf" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="var(--cyan)"/></marker></defs>']

    def box(x, y, w, h, t, s="", cls="dv", fs=12.5):
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" class="{cls}"/>')
        tc, sc = ("sft-w", "sfs-w") if cls == "sfres" else ("dvt", "dvs")
        o.append(f'<text x="{x + w / 2}" y="{y + h / 2 + (4 if not s else -3)}" class="{tc}" font-size="{fs}">{E(t)}</text>')
        if s:
            o.append(f'<text x="{x + w / 2}" y="{y + h / 2 + 13}" class="{sc}">{E(s)}</text>')

    def arr(pts, t="", tx=None, ty=None, anchor="middle"):
        o.append(f'<polyline points="{" ".join(f"{a},{b}" for a, b in pts)}" class="fl-d" stroke-width="2" marker-end="url(#cf)"/>')
        if t:
            o.append(f'<text x="{tx}" y="{ty}" class="fl-t" text-anchor="{anchor}" font-weight="700">{E(t)}</text>')

    o.append('<text x="20" y="22" class="sfh">❶ 로컬 보관량 + 여유 → 필요 용량</text>')
    o.append('<text x="1100" y="266" class="sfh" text-anchor="end">❷ Ceph 사용률·이레이저 코딩 → 스토리지 노드 수</text>')
    o.append('<rect x="10" y="34" width="1100" height="196" rx="8" class="sflane"/>')
    o.append('<rect x="10" y="274" width="1100" height="146" rx="8" class="sflane"/>')
    # ❶
    box(20, 102, 190, 60, f"존 원시 {MONTH_TB:.0f} TB/월", "② 셀별 발생량 합계 (5셀)", "dv2", 13.5)
    arr([(210, 132), (232, 132), (232, 76), (258, 76)])
    arr([(210, 132), (232, 132), (232, 188), (258, 188)])
    box(260, 46, 290, 60, f"raw 버킷 {RAW_TB:,.0f} TB", f"{MONTH_TB:.0f} TB × {RET_M}개월 로컬 보관")
    box(260, 158, 290, 60, f"ai-ready 버킷 {AIR_TB:,.0f} TB", f"{MONTH_TB:.0f} × {AIR_RATIO * 100:.0f}% = {air_m:.1f} TB/월 × {AIR_RET}개월")
    arr([(550, 76), (574, 76), (574, 132), (598, 132)])
    arr([(550, 188), (574, 188), (574, 132), (598, 132)])
    o.append('<text x="584" y="122" class="fl-t" text-anchor="middle" font-weight="700">합</text>')
    box(600, 102, 190, 60, f"보관량 {keep:,.0f} TB", f"{RAW_TB:,.0f} + {AIR_TB:,.0f}", "dv2", 13.5)
    arr([(790, 132), (858, 132)], "× 1.3", 824, 123)
    box(860, 96, 240, 72, f"필요 용량 {NEED_TB:,.0f} TB", f"{keep:,.0f} × 1.3 (메타데이터·여유)", "sfres", 15)
    # ❷
    arr([(980, 168), (980, 246), (145, 246), (145, 290)])
    box(20, 292, 250, 64, f"÷ {FILL} → usable {usable_need:,.0f} TB", f"Ceph 권장 사용률 {FILL * 100:.0f}% 이하 유지")
    arr([(270, 324), (348, 324)])
    box(350, 292, 330, 64, f"÷ {NODE_USABLE:.0f} TB = {usable_need / NODE_USABLE:.1f} → 올림 {N_STO}대", f"{usable_need:,.0f} ÷ 노드당 usable {NODE_USABLE:.0f} TB")
    box(350, 368, 330, 44, f"노드 1대 usable {NODE_USABLE:.0f} TB", f"12 × 20TB = {NODE_RAW} TB × 4/6 (EC 4+2)", "dv3", 12)
    arr([(515, 368), (515, 358)])
    arr([(680, 324), (758, 324)])
    box(760, 288, 340, 72, f"STO {N_STO}대 · usable {N_STO * NODE_USABLE:,.0f} TB", f"사용률 {NEED_TB / (N_STO * NODE_USABLE) * 100:.0f}% (필요 {NEED_TB:,.0f} ÷ {N_STO * NODE_USABLE:,.0f})", "sfres", 15)
    o.append('<text x="760" y="386" class="sfn">중앙 Server에는 ai-ready만 전송함.</text>')
    o.append('<text x="760" y="404" class="sfn">raw·ai-ready는 3개월 보관 후 로컬에서 삭제함.</text>')
    o.append("</svg>")
    return '<figure class="fig" style="margin:10px 0 14px">' + "".join(o) + "</figure>"


def sizing_table():
    spec = []
    spec.append('<tr class="grp"><th colspan="5">로봇 구성 (셀당)</th></tr>')
    spec.append(f'<tr><td class="nm">셀당 로봇 {N_ROBOT}대</td><td class="spec">' + " · ".join(f"{n} {q}대" for n, q in ROBOTS) + f'</td><td class="num">–</td><td class="num">–</td><td class="note">카메라 = 로봇당 3대(손목 D405·머리/가슴 D455) + 협동로봇 엑소센트릭 D455 {N_EXO}대 → 셀당 {N_CAM}대</td></tr>')
    spec.append('<tr class="grp"><th colspan="5">카메라 1대당 기록 사양</th></tr>')
    for name, sp, mbps, note in CAMS:
        spec.append(f'<tr><td class="nm">{E(name)}</td><td class="spec">{E(sp)}</td><td class="num">{mbps:.1f} Mbps</td><td class="num">{tb_month(mbps):.2f} TB/월</td><td class="note">{E(note)}</td></tr>')
    spec.append(f'<tr class="tot"><th>로봇 1대 카메라 합계</th><td class="spec">손목 + 머리 + 가슴 (모든 로봇)</td><td class="num">{CAM_MBPS:.1f} Mbps</td><td class="num">{tb_month(CAM_MBPS):.2f} TB/월</td><td></td></tr>')
    spec.append(f'<tr><td class="nm">{E(EXO[0])}</td><td class="spec">{E(EXO[1])}</td><td class="num">{EXO[2]:.1f} Mbps</td><td class="num">{tb_month(EXO[2]):.2f} TB/월</td><td class="note">{E(EXO[3])}</td></tr>')
    spec.append('<tr class="grp"><th colspan="5">로봇 1대당 텔레메트리</th></tr>')
    for name, sp, bps in TEL:
        spec.append(f'<tr><td class="nm">{E(name)}</td><td class="spec">{E(sp)}</td><td class="num">{bps / 1000:.0f} KB/s</td><td class="num">{tb_month(bps * 8 / 1e6):.2f} TB/월</td><td class="note"></td></tr>')
    spec_tbl = ('<div class="tbl-wrap"><table class="bom"><thead><tr><th>항목</th><th>사양 (기록 기준)</th><th style="text-align:right">대역폭</th><th style="text-align:right">월 발생량</th><th>비고</th></tr></thead>'
                f'<tbody>{"".join(spec)}</tbody></table></div>')
    rows = []
    for r in SZ:
        rows.append(f'<tr><td><b>{r["id"]}</b></td><td class="q">{r["rob"]}</td><td class="q">{r["cam"]}</td>'
                    f'<td class="num">{r["cam_mbps"] + r["tel_mbps"]:.0f}</td><td class="num">{r["tags"]:,}</td><td class="num">{r["video"]:.1f}</td>'
                    f'<td class="num">{r["tel"]:.2f}</td><td class="num"><b>{r["tot"]:.1f}</b></td></tr>')
    rows.append(f'<tr class="grp"><th>존 합계 (5셀)</th><td class="q">{sum(r["rob"] for r in SZ)}</td><td class="q">{sum(r["cam"] for r in SZ)}</td><td class="num">{sum(r["cam_mbps"] + r["tel_mbps"] for r in SZ):,.0f}</td>'
                f'<td class="num">{sum(r["tags"] for r in SZ):,}</td><td class="num">{sum(r["video"] for r in SZ):.1f}</td>'
                f'<td class="num">{sum(r["tel"] for r in SZ):.2f}</td><td class="num">{MONTH_TB:.1f}</td></tr>')
    res_tbl = ('<div class="tbl-wrap"><table class="bom"><thead><tr><th>셀</th><th style="text-align:center">로봇</th><th style="text-align:center">카메라</th><th style="text-align:right">평균 대역폭 Mbps</th>'
               '<th style="text-align:right">AAS 태그(추정)</th><th style="text-align:right">카메라 영상 TB/월</th><th style="text-align:right">텔레메트리 TB/월</th><th style="text-align:right">합계 TB/월</th></tr></thead>'
               f'<tbody>{"".join(rows)}</tbody></table></div>')
    return '<h3>① 산정 기준 장비 사양</h3>' + spec_tbl + '<h3>② 셀별 발생량</h3>' + size_flow_svg() + res_tbl + '<h3>③ 필요 저장 용량</h3>' + cap_flow_svg()


DEV_SYMS = ("AASIM", "RAW", "ETL", "OCS", "TRC", "AASR", "LAKE", "FS", "CAT", "MON")
DEV = sum(P[k][2] for k in DEV_SYMS)


ROLES = [
    ("LS-1 · LS-2 · LS-3", "LS", "3대 (한 묶음)",
     "같은 역할을 하는 Kubernetes HA 클러스터. 존 SW 약 20개를 세 대에 나눠 돌리고 1대가 고장 나면 나머지 2대로 자동 재배치",
     "AAS Repository·Registry · Operational TSDB(Machbase) · MQTT 브로커 · 존 오케스트레이터(OCS) · Airflow 파이프라인 제어 · Feature Store · 카탈로그 · 모니터링 · 보안 · TTA Trace API",
     "etcd 과반수 판단에 최소 3노드 필요. AAS·TSDB·MQTT는 3중 복제. 노드별 주 배치는 운영 시 LS-1 AAS·OCS / LS-2 TSDB·MQTT / LS-3 파이프라인·카탈로그·모니터링으로 둠(설계)"),
    ("GPU-1", "GPU", "1대",
     "실시간 추론. 셀 상태머신의 HOLD·재시도·격리 판단 모델, 결합 OK/NG 판정 모델, 재계획 모델 서비스",
     "Triton Inference Server (오픈소스)",
     "이상 판단 10초 KPI를 지키려면 배치 작업과 GPU를 나눠 써야 함"),
    ("GPU-2", "GPU", "1대",
     "배치 연산. AI Ready 변환의 GPU 단계(영상 디코딩·동기 정렬), 작업자 영상 비식별, 사전 라벨링, 합성데이터 생성, 모델 재학습",
     "Airflow 파이프라인 GPU 작업 · Isaac Sim/Lab 연산 보조",
     "대용량 배치가 실시간 추론 지연을 일으키지 않도록 분리"),
    ("OWS ×2", "OWS", "2대",
     "운영 관제. 1대는 존 전체(OCS 화면·셀 상태·배치 진척·KPI), 1대는 셀 알람 대응(HOLD 승인·셀 재배정·이상 이력)",
     "존 오케스트레이터 UI · 모니터링 대시보드",
     "운영자 2명이 동시에 작업. GPU 불필요해 고성능 PC로 구성"),
    ("DWS ×2", "DWS", "2대",
     "디지털트윈. 1대는 DMWorks 검증 DT(지그·공정 투입 전 경로 간섭·사이클타임 가상 시운전, PLC 시퀀스 검증), 1대는 Isaac Sim 학습 DT(VLA·스킬 학습 씬, S2R 정합)",
     "DMWorks · Isaac Sim/Lab",
     "라이선스와 3D GPU 부하가 겹치지 않게 분리. RTX PRO 6000 탑재"),
]


def roles_table():
    body = "".join(f'<tr><th scope="row"><a href="#hw-{sym}" class="tolink">{E(n)}</a></th><td class="u">{E(q)}</td><td>{E(r)}</td><td>{E(sw)}</td><td class="note">{E(why)}</td></tr>'
                   for n, sym, q, r, sw, why in ROLES)
    return ('<div class="tbl-wrap"><table class="bom issuetbl"><thead><tr><th>장비</th><th>수량</th><th>용도</th><th>탑재 SW</th><th>나눈 이유</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>')


def summary_svg():
    cell_mbps = SZ[0]["cam_mbps"] + SZ[0]["tel_mbps"]
    zone_g = sum(r["cam_mbps"] + r["tel_mbps"] for r in SZ) / 1000
    cap = N_STO * NODE_USABLE
    stages = [
        ("현장 (실증 존별 셀)", ["로봇 · AMR · 카메라", "PLC · F/T · 센서", "FieldBus · AAS"], "ly4"),
        ("Edge Gateway (셀별)", ["EGW (OPC UA · AAS 매핑)", "영상 수집 노드 (영상 AI)", "시계열 · 영상 버퍼"], "ly3"),
        ("Local Server (존별)", ["로컬 서버 · GPU · 스토리지", "Data Lake · TSDB · AAS", "DT · 존 오케스트레이터"], "ly2"),
        ("중앙 Server", ["Enterprise AAS · Data Lake", "AI Model Registry", "D-1-1 · D-2-1"], "ly1"),
    ]
    arrows = ["OPC UA · 영상 스트림", "원시데이터 (존 내 보관)", "AI Ready 데이터 (MQTT/REST)"]
    W, bw, gap = 1120, 220, 72
    o = [f'<svg class="arch plan" viewBox="0 0 {W} 226" role="img" aria-label="존별 OCS Cell 공통 데이터 흐름" style="max-width:1120px">',
         '<defs><marker id="sm" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="var(--cyan)"/></marker></defs>']
    for n, (title, lines, cls) in enumerate(stages):
        x = 12 + n * (bw + gap)
        o.append(f'<rect x="{x}" y="34" width="{bw}" height="150" rx="8" class="ly {cls}"/>')
        o.append(f'<text x="{x + 14}" y="62" class="lyt">{E(title)}</text>')
        for k_, ln in enumerate(lines):
            o.append(f'<rect x="{x + 12}" y="{76 + k_ * 34}" width="{bw - 24}" height="28" rx="4" class="box"/>')
            o.append(f'<text x="{x + bw / 2}" y="{95 + k_ * 34}" class="boxt" font-size="12">{E(ln)}</text>')
        if n < 3:
            ax = x + bw + 4
            o.append(f'<line x1="{ax}" y1="109" x2="{ax + gap - 8}" y2="109" class="fl-d" stroke-width="3" marker-end="url(#sm)"/>')
            o.append(f'<text x="{ax + (gap - 4) / 2}" y="218" class="fl-t" text-anchor="middle" font-size="11">{E(arrows[n])}</text>')
            o.append(f'<line x1="{ax + (gap - 4) / 2}" y1="206" x2="{ax + (gap - 4) / 2}" y2="118" class="fl-c" stroke-width="1"/>')
    o.append('<rect x="4" y="24" width="236" height="170" rx="10" class="fld"/>')
    o.append('<text x="122" y="16" class="fldtag" text-anchor="middle">현장 — 실증 존별 셀</text>')
    o.append('<rect x="296" y="24" width="528" height="170" rx="10" class="own"/>')
    o.append('<text x="560" y="16" class="owntag" text-anchor="middle">존별 OCS Cell 범위 — 모든 실증 존 공통</text>')
    o.append("</svg>")
    return '<figure class="fig" style="margin:10px 0 14px">' + "".join(o) + "</figure>"


def summary_table():
    cap = N_STO * NODE_USABLE
    rows = [
        ("역할", "현장 데이터를 Edge Gateway에서 OPC UA로 모아 AAS로 매핑하고, Local Server에서 원시데이터·운영 시계열·AAS를 저장한 뒤 AI Ready 데이터로 바꿔 중앙 Server로 보냄 [D1]. 디지털트윈·존 오케스트레이터도 같은 Local Server 데이터를 씀 (설계) [W9]", ""),
        ("계층 배치", "Local Server → 존 서버실 랙 3개(연산·네트워크·스토리지) · 방화벽 HA 쌍 · 코어 스위치 MLAG 2대 / Edge Gateway(OPC UA)·영상 수집 노드 → 셀 캐비닛 / 셀–서버실 10GbE 이중 광 + PTP 시간동기", ""),
        ("수집 경로", "① 상태·공정값: OPC UA → Edge TSDB → Operational TSDB ② 영상·진동·오디오 대용량: OPC UA 우회 → S3 → Data Lake", "D1"),
        ("실시간 제어", "OPC UA 지연(약 100ms) 때문에 로봇·서보 제어는 셀 PLC EtherCAT에 둠. OCS Cell은 수집·감독·재계획만 맡음", "W8"),
        ("산정 기준", f"셀당 협동로봇 10 · AMR 4 · AMMR 1 = 로봇 {N_ROBOT}대, 로봇별 카메라 3대(손목 D405·머리/가슴 D455) + 협동로봇 엑소센트릭 D455 = 셀당 {N_CAM}대, 월 {OPS_H}h 연속 기록", ""),
        ("데이터량", f"셀당 {SZ[0]['cam_mbps'] + SZ[0]['tel_mbps']:.0f}Mbps · 월 {SZ[0]['tot']:.1f}TB → 존 월 {MONTH_TB:,.0f}TB (카메라 영상 98%)", ""),
        ("저장", f"{RET_M}개월 보관 필요 {NEED_TB:,.0f}TB → 20TB×12 스토리지 노드 {N_STO}대, usable {cap:,.0f}TB (Ceph 사용률 80% 이내)", ""),
        ("규모·금액", f"존 HW {len(HW)}종 · 존 SW {len(SW)}종 {k(total(HW) + total(SW))}천원 + 셀 HW·SW(온디바이스 엣지 75대) 별도 (VAT 별도, 총액 요약 참조)", ""),
        ("주요 쟁점", "협약 품목 부재(예산 출처) · Edge Gateway·AI Ready 파이프라인 개발 주체 미정 · AAS 서브모델 캠틱 정의 필요 · 보관 기간(1개월 시 스토리지 6대)", ""),
    ]
    body = "".join(f'<tr><th scope="row">{E(a)}</th><td>{E(b)}{(" [" + c + "]") if c else ""}</td></tr>' for a, b, c in rows)
    return f'<div class="tbl-wrap"><table class="sumtbl"><tbody>{body}</tbody></table></div>'


CELL_HW_SW = {
    "EDGE-T": ["JP", "ROS", "BRG", "VLA-R", "SAFE-AI", "EPI", "OTA", "MONA", "ESEC"],
    "EDGE-O": ["JP", "ROS", "EPI", "UPL", "OTA", "MONA", "ESEC"],
    "NPU-M": ["DXNN"],
}
N_CELL = 5


def clinks(sym):
    ls = CELL_SRC.get(sym, [])
    return "<br>".join(f'<a href="{E(u)}" target="_blank" rel="noopener">{E(t)} ↗</a>' for t, u in ls)


def cell_qty_total(sym, q, unit):
    # 개발·구축 '식'과 소프트웨어 카피는 존 전체 1회, 장비는 셀당 수량 × 5셀
    if unit == "식" and sym not in ("KIT",):
        return q
    if sym in ("JP", "ROS", "OTA", "MONA", "DXNN"):
        return q
    return q * N_CELL


def cell_hw_table():
    head = ("<tr><th>기호</th><th>품목</th><th>주요 스펙</th><th>추천 제품·모델</th><th>제조사 (국가)</th><th>셀당</th><th>5셀 합계</th><th>단위</th>"
            "<th>단가</th><th>5셀 금액</th><th>기능</th><th>용도</th><th>가격 근거</th><th>사양·가격 출처</th></tr>")
    body, cur, tot, tot_new = [], None, 0, 0
    for g, sym, name, spec, q, unit, func, use, bom in CELL_HW:
        if g != cur:
            cur = g
            body.append(f'<tr class="grp"><th colspan="14" scope="rowgroup">{E(g)}</th></tr>')
        prod, maker, up, basis = CELL_P[sym]
        qt = cell_qty_total(sym, q, unit)
        amt = up * qt
        tot += amt
        if "미포함" in bom:
            tot_new += amt
        sws = CELL_HW_SW.get(sym, [])
        if sws:
            ids = ",".join("csw-" + x for x in sws)
            nm = f'<a href="#csw-{sws[0]}" class="tolink sw" data-flash="{ids}">{E(name)}</a><span class="where">탑재 셀 SW {len(sws)}종 ↓</span>'
        else:
            nm = E(name)
        if sym in ("EDGE-T", "EDGE-O"):
            nm += f' <a href="#topo-{sym}" class="tolink">도면 ↑</a>'
        body.append(f'<tr id="chw-{sym}"><td class="sym">{E(sym)}</td><td class="nm">{nm}</td><td class="spec">{E(spec)}</td><td class="prod">{E(prod)}</td>'
                    f'<td class="mk">{E(maker)}</td><td class="q">{q}</td><td class="q"><b>{qt}</b></td><td class="u">{E(unit)}</td>'
                    f'<td class="num">{k(up)}</td><td class="num">{k(amt)}</td><td>{E(func)}</td><td>{E(use)}</td>'
                    f'<td class="note">{E(basis)}</td><td class="src">{clinks(sym)}</td></tr>')
    foot = f'<tr class="tot strong"><th colspan="9">셀 HW 합계 (5셀)</th><td class="num">{k(tot)}</td><td colspan="4">셀당 약 {k(tot / N_CELL)}천원</td></tr>'
    return f'<div class="tbl-wrap"><table class="bom wide"><thead>{head}</thead><tbody>{"".join(body)}</tbody><tfoot>{foot}</tfoot></table></div>', tot, tot_new


def cell_sw_table():
    head = ("<tr><th>기호</th><th>품목</th><th>주요 스펙</th><th>추천 제품·방식</th><th>제공 (국가)</th><th>수량</th><th>단위</th>"
            "<th>단가</th><th>금액</th><th>기능</th><th>Use Case (정밀조립존 적용 예)</th><th>가격 근거</th><th>출처</th></tr>")
    body, cur, tot, tot_new = [], None, 0, 0
    for g, sym, name, spec, q, unit, func, use, node, bom in CELL_SW:
        if g != cur:
            cur = g
            body.append(f'<tr class="grp"><th colspan="13" scope="rowgroup">{E(g)}</th></tr>')
        prod, maker, up, basis = CELL_P[sym]
        amt = up * q
        tot += amt
        if "미포함" in bom:
            tot_new += amt
        where = "협동로봇·AMMR 엣지" if node == "EDGE-T" else "AMR 엣지"
        nm = f'<a href="#topo-{node}" class="tolink sw">{E(name)}</a><span class="where">설치: {where} ↑</span>'
        body.append(f'<tr id="csw-{sym}"><td class="sym">{E(sym)}</td><td class="nm">{nm}</td><td class="spec">{E(spec)}</td><td class="prod">{E(prod)}</td>'
                    f'<td class="mk">{E(maker)}</td><td class="q"><b>{q}</b></td><td class="u">{E(unit)}</td><td class="num">{k(up) if up else "0"}</td>'
                    f'<td class="num">{k(amt)}</td><td>{E(func)}</td><td class="uc">{E(use)}</td><td class="note">{E(basis)}</td>'
                    f'<td class="src">{clinks(sym)}</td></tr>')
    foot = f'<tr class="tot strong"><th colspan="8">셀 SW 합계 (5셀 공통 개발 1회 기준)</th><td class="num">{k(tot)}</td><td colspan="4"></td></tr>'
    return f'<div class="tbl-wrap"><table class="bom wide"><thead>{head}</thead><tbody>{"".join(body)}</tbody><tfoot>{foot}</tfoot></table></div>', tot, tot_new


def price_summary(chw_tot, chw_new, csw_tot, csw_new):
    zh, zs = total(HW), total(SW)
    rows = [
        ("존 HW", f"{len(HW)}종", zh, "존 서버실·관제실·셀 캐비닛 장비 (OCS Cell)", "#hw"),
        ("존 SW", f"{len(SW)}종", zs, "Edge Gateway·로컬 서버·DT 소프트웨어 (OCS Cell)", "#sw"),
        ("셀 HW", f"{len(CELL_HW)}종", chw_tot, "온디바이스 엣지 75대·부속", "#chw"),
        ("셀 SW", f"{len(CELL_SW)}종", csw_tot, "모두 무료 플랫폼 또는 연구 인력 자체 개발 0원", "#csw"),
    ]
    body = "".join(f'<tr><th scope="row"><a href="{h}" class="tolink">{E(a)}</a></th><td class="q">{c}</td><td class="num">{k(v)}</td><td class="note">{E(n)}</td></tr>'
                   for a, c, v, n, h in rows)
    zone, cell = zh + zs, chw_tot + csw_tot
    body += (f'<tr class="tot"><th scope="row">존 소계 (OCS Cell)</th><td></td><td class="num">{k(zone)}</td><td class="note">존 HW + 존 SW</td></tr>'
             f'<tr class="tot"><th scope="row">셀 소계 (온디바이스 엣지)</th><td></td><td class="num">{k(cell)}</td><td class="note">셀 HW + 셀 SW</td></tr>'
             f'<tr class="tot strong"><th scope="row">총계</th><td></td><td class="num">{k(zone + cell)}</td><td class="note">존 소계 + 셀 소계</td></tr>')
    return ('<div class="tbl-wrap"><table class="bom"><thead><tr><th>구분</th><th style="text-align:center">품목 수</th><th style="text-align:right">총액 (천원)</th><th>비고</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>')


ISSUES = [
    ("예산", "예산 출처", "협약 계획에 정밀조립존 OCS Cell 품목이 없음. 금액은 상용 장비·라이선스 기준", "편성 근거가 없으면 구매 불가", "예산 편성 근거 마련, NIPA 협의"),
    ("예산", "견적 미확보 품목", "[추정] 단가 다수. 금액 영향이 큰 것은 Thor 산업용 엣지(MIC-743) 55대, KTNF 서버·스토리지 12대, 방화벽·PTP·항온항습기", "총액 오차가 큼", "제조사가 다른 비교견적 2건 확보"),
    ("네트워크", "5G 모뎀", "AMR·AMMR 25대에 5G 모뎀(XR60, n79) 추가. 5G 기지국·코어는 이음5G 별도로 제외", "이음5G 망 미구축 시 Wi-Fi 6E만 사용", "국내 전파인증(KC)·이음5G 단말 등록 확인, 망 구축 주체·일정 확인, SIM·통신 요금 별도 편성"),
    ("인력", "자체 개발 인력", "존·셀 SW 개발·구축 15종을 연구 인력 자체 개발(0원)로 정함. 9/21 회의에서 Edge Gateway·AI Ready 파이프라인 구현 팀 부재 리스크 [높음] 제기 [W8]", "인력 부족 시 일정 지연", "담당 인력·일정 확정"),
    ("기술", "AAS 규격", "서브모델·Semantic ID를 캠틱이 정의해야 함(DMWorks·유일로보틱스 모두 자체 템플릿 없음)", "데이터 표준화·중앙 연계 지연", "TTA 표준 템플릿·힌지큐브 자문(10/16·11/6·12/4)으로 1차 정의안"),
    ("기술", "영상 수집 노드 GPU", "SYS-E403-14B 스토어 페이지에는 GPU 지원 목록에 RTX 3060만 표시", "L4 미지원 시 사양 변경", "공급사에 L4 장착 지원 확인"),
    ("데이터", "보관 정책", f"원시데이터 {RET_M}개월 + AI Ready {AIR_RET}개월 로컬 보관(필요 {NEED_TB:,.0f}TB, 스토리지 {N_STO}노드). 9/21 회의는 원시 약 1개월 언급", f"1개월이면 약 {NEED_1M:,.0f}TB·6노드로 감소", "보관 기간 결정"),
    ("기술", "장비 통신 방식", "OPC UA 수집을 오픈소스(open62541·PLC4X)로 자체 구성, Kepware 미사용", "고유 프로토콜 장비가 많으면 드라이버 개발 부담 증가", "셀 장비 발주 사양에 'OPC UA 서버 내장 또는 Modbus·EtherNet/IP 지원' 명시, 예외 장비는 Kepware 1~2카피로 보완"),
    ("데이터", "데이터량 가정", "카메라 비트레이트·Depth 기록·운용 중 연속 기록·검사 카메라 제외를 가정", f"Depth를 기록하지 않으면 월 약 {tb_month(N_CAM * 4 + SZ[0]['tel_mbps']) * len(SZ):,.0f}TB, 지금 가정은 {MONTH_TB:,.0f}TB로 가정에 따라 크게 변동", "카메라 설정·기록 정책 확정 후 재산정"),
    ("연계", "중앙 연계", "중앙 Server(AAS 통합서버 D-1-1)가 GPU를 뺀 스토리지 컨셉으로 재견적 중(10/7)", "추론 역할 중복·공백", "로컬 GPU 서버(추론)와 역할 경계 합의"),
    ("설치", "서버실 여건", f"존 서버실 28.8㎡에 랙 3개·UPS·항온항습기, 부하 약 {2.4 + 4.0 + N_STO * 0.5 + 1.3:.0f}kW", "전력·하중 부족 시 위치 변경", "전력·하중·층고 실측"),
]


def issues_table():
    body = "".join(f'<tr><td class="u">{E(a)}</td><th scope="row">{E(b)}</th><td>{E(c)}</td><td>{E(d)}</td><td>{E(e)}</td></tr>' for a, b, c, d, e in ISSUES)
    return ('<div class="tbl-wrap"><table class="bom issuetbl"><thead><tr><th>구분</th><th>쟁점</th><th>현재 안·상황</th><th>영향</th><th>다음 조치</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>')


REFS = [
    ("D1", "내부 자료", "2-2. 피지컬AI 제조 데이터 구축(4/6) — 피지컬AI를 위한 AAS 기반 데이터 수집-저장 표준 아키텍처(안)", "-", "바탕화면 데이터수집.png",
     "요약표 역할·수집 경로, 논리 구성도"),
    ("W8", "llm-wiki", "엣지·로컬 DCC 데이터 계층 · AAS 기반 DT 데이터 수집 설계 원칙(힌지큐브: 장비당 약 400 엘리먼트, 20ms/200ms/1~3s, 타임싱크 필수) · 테스트베드 스토리지 아키텍처(S3+NFS 병행)",
     "2026-09-17 · 09-21 · 09-22", "llm-wiki concepts", "실시간 제어 분리, AAS 태그 수, 자체 개발 인력 리스크"),
    ("W9", "llm-wiki", "피지컬AI 의사결정 미팅 — \"OCS 셀 = 존 오케스트레이터 겸 로컬 서버\" · 정밀조립 Zone 운영 시나리오 수정 v3 — 로컬 오케스트레이터 = Manufacturing Agent, DT 검증 계층",
     "2026-10-06", "llm-wiki sources", "요약표 역할(디지털트윈·존 오케스트레이터)"),
    ("-", "작업 산출물", "셀 구성·현장 장비 수: 정밀조립존 셀 구성 계획(같은 세션 산출물)", "2026-10-07", "정밀조립존 셀 구성 계획 페이지", "존 배치도, 셀별 공정설비 수"),
]


def refs_table():
    body = "".join(f'<tr><td class="sym">{("[" + a + "]") if a != "-" else "-"}</td><td class="u">{E(b)}</td><td>{E(c)}</td><td class="u">{E(d)}</td><td class="note">{E(e)}</td><td class="note">{E(f)}</td></tr>'
                   for a, b, c, d, e, f in REFS)
    return ('<div class="tbl-wrap"><table class="bom"><thead><tr><th>표기</th><th>구분</th><th>문서·내용</th><th>일자</th><th>위치</th><th>이 페이지에서 쓴 곳</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>')


def cost_summary():
    h, w = total(HW), total(SW)
    return ('<div class="tbl-wrap" style="max-width:520px"><table class="sum"><thead><tr><th>구분 (VAT 별도)</th><th>HW</th><th>SW</th><th>합계</th></tr></thead>'
            f"<tbody><tr><td>추정 금액 (천원)</td><td class='num'>{k(h)}</td><td class='num'>{k(w)}</td><td class='num'><b>{k(h + w)}</b></td></tr></tbody></table></div>")


def page():
    cap = N_STO * NODE_USABLE
    CHW_TABLE, chw_tot, chw_new = cell_hw_table()
    CSW_TABLE, csw_tot, csw_new = cell_sw_table()
    return f'''<title>로컬 OCS Zone 구성 - (예시) 정밀조립존</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&family=IBM+Plex+Mono:wght@400;500&display=swap">
{CSS}{EXTRA}
<header class="mast"><div class="wrap">
  <p class="eyebrow">총괄5-세부1 · A-3 정밀조립(Micro) Zone · 피지컬AI 제조 데이터 구축(2-2) 수집–저장 표준 아키텍처 적용 · 2026.10.07 작성 · 설계 추정본</p>
  <h1>로컬 OCS Zone 구성 - (예시) 정밀조립존</h1>
</div></header>
<nav class="toc" aria-label="바로가기"><div class="wrap">
  <a href="#sum">요약</a><a href="#logic">논리 구성도</a><a href="#topo">연결 토폴로지</a><a href="#floor">설치 배치</a>
  <a href="#size">데이터량</a><a href="#price">총액</a><a href="#hw">존 HW</a><a href="#sw">존 SW</a><a href="#chw">셀 HW</a><a href="#csw">셀 SW</a><a href="#issues">확인 필요</a><a href="#refs">근거</a>
</div></nav>
<main class="wrap">
<section class="summary" id="sum" style="margin-top:8px">
  <p class="eyebrow">결론 및 핵심 요약 (Executive Summary)</p>
  <h2>존별 Local Server + 셀별 Edge Gateway·영상 수집 노드</h2>
  {summary_svg()}
  <h3>정밀조립존 적용 요약</h3>
  {summary_table()}
</section>

<section id="logic">
  <p class="eyebrow">1. 논리 구성</p>
  <h2>AAS 기반 수집–저장 공통 아키텍처</h2>
  <figure class="fig">{logical_svg()}<figcaption>바탕은 「2-2. 피지컬AI 제조 데이터 구축 — AAS 기반 데이터 수집-저장 표준 아키텍처(안)」. 모든 실증 존이 같은 계층 구조로 존마다 OCS Cell(주황 테두리: Local Server + Edge Gateway)을 두고 중앙 Server와 TTA 검증 영역에 연계함. 초록 테두리는 현장(실증 존별 셀)임. 청록 강조는 이 페이지의 예시인 정밀조립 존임. 아래 연결 토폴로지·설치 배치·데이터량·HW·SW 목록은 이 공통 구조를 정밀조립존에 적용한 예시임.</figcaption></figure>
</section>

<section id="topo">
  <p class="eyebrow">2. 물리 연결 토폴로지</p>
  <h2>장비 설치·연결 구성</h2>
  <figure class="fig">{topo_svg()}{legend_topo()}
  <figcaption>모든 서버·스토리지·방화벽·관제실·셀 캐비닛은 CORE-1(실선)과 CORE-2(점선)에 1회선씩 연결한 MLAG 이중 구성임. <b>장비 노드를 누르면 존 HW(셀 내부 로봇 CTRL·AMR 노드는 셀 HW)의 해당 품목으로 이동함(강조는 다음 클릭 때 해제).</b> 각 표의 “도면 ↑”와 SW 품목명을 누르면 이 도면의 설치 노드로 돌아옴. 최종 구성(5셀 완성 기준)임. 셀 내부 장비(PLC·서보·카메라·F/T)는 연결 관계를 보이기 위해 함께 그렸음.</figcaption></figure>
  <h3>주요 서버·워크스테이션 용도</h3>
  {roles_table()}
</section>

<section id="floor">
  <p class="eyebrow">3. 설치 배치</p>
  <h2>창조2관 2층 설치 위치</h2>
  <figure class="fig">{floor_svg()}
  <ul class="lg"><li><svg width="16" height="12"><rect width="16" height="12" class="cabf"/></svg>셀 캐비닛</li>
  <li><svg width="16" height="12"><circle cx="6" cy="6" r="6" class="apf"/></svg>Wi-Fi 6E AP</li><li><svg width="30" height="10"><line x1="0" y1="5" x2="30" y2="5" class="tray-l" style="stroke-width:6"/></svg>케이블 트레이</li>
  <li><svg width="16" height="12"><rect width="16" height="12" class="rackf"/></svg>서버 랙 A·B</li></ul>
  <figcaption>존 배치도(정밀조립존 셀 구성 계획)의 엣지 서버·네트워크실과 로컬존 DCC 관제실을 OCS Cell 설치 공간으로 씀(주황 테두리). 랙·트레이 경로는 실측 후 확정함.</figcaption></figure>
</section>

<section id="size">
  <p class="eyebrow">4. 데이터량 산정</p>
  <h2>셀별 원시데이터 발생량과 저장 용량</h2>
  {sizing_table()}
</section>

<section id="price">
  <p class="eyebrow">총액 요약</p>
  <h2>존·셀 HW·SW 총액</h2>
  <p class="note-box">단위 천원, VAT 별도. 구분명을 누르면 해당 목록으로 이동함.</p>
  {price_summary(chw_tot, chw_new, csw_tot, csw_new)}
</section>

<section id="hw">
  <p class="eyebrow">5. 존 HW</p>
  <h2>존 HW 품목·수량·용도·추천 제품·가격</h2>
  <p class="note-box">품목명을 누르면 그 장비에 설치되는 존 SW 품목으로 이동하고 해당 SW 행이 모두 강조됨. “도면 ↑”는 연결 토폴로지의 노드로 이동함.</p>
  <p class="note-box">단가·금액 단위 천원, VAT 별도. 가격 근거 등급(2026-10-07 재확인): <b>[공개가·확인]</b> 링크 페이지를 직접 열어 가격·사양을 확인함 · <b>[공개가·검색]</b> 판매처가 자동 접속을 막아 검색 결과 요약으로만 확인함(브라우저 재확인 필요) · <b>[견적]</b> 내부 견적·정가표 · <b>[추정]</b> 공개 가격 없음(견적 필요). 해외가는 {FX} 환산이며 국내 유통 마진·관세는 반영하지 않음. 중국 기업 제품은 넣지 않았음.</p>
  {item_table(HW)}
</section>

<section id="sw">
  <p class="eyebrow">6. 존 SW</p>
  <h2>존 SW 품목·수량·용도·Use Case·추천 제품·가격</h2>
  <p class="note-box">상용 라이선스(Machbase·DMWorks·HIWARE)만 금액을 잡았음. 오픈소스 기반 개발·구축 항목(open62541·PLC4X·RKE2·Triton·RabbitMQ 등)은 연구 인력 자체 개발(인건비 처리)로 0원임. 연 구독형 SW는 없음.</p>
  {item_table(SW, with_loc=False)}
</section>

<section id="chw">
  <p class="eyebrow">7. 셀 HW — 온디바이스 엣지</p>
  <h2>셀 HW 품목·수량·기능·용도·사양·가격</h2>
  <p class="note-box">로봇마다 붙는 온디바이스 엣지와 부속임. 셀당 협동로봇 10 + AMMR 1 = Thor급 11대, AMR 4 = Orin급 4대 → 5셀 75대. 단가·금액 단위 천원, VAT 별도. 품목명을 누르면 탑재 셀 SW로, “도면 ↑”는 토폴로지의 로봇 CTRL·AMR 노드로 이동함.</p>
  {CHW_TABLE}
</section>

<section id="csw">
  <p class="eyebrow">8. 셀 SW — 온디바이스 엣지</p>
  <h2>셀 SW 품목·기능·Use Case·사양·가격</h2>
  <p class="note-box">엣지에 설치되는 소프트웨어. 무료 플랫폼은 엣지 대수만큼 설치함. 로봇 제어 브리지·VLA 추론 런타임·안전 이상 감지 모델·에피소드 기록기·업로드 에이전트·엣지 보안 설정은 오픈소스 기반으로 연구 인력이 자체 개발·구축해 모두 0원(인건비 처리)으로 둠. 품목명을 누르면 설치 노드로 이동함.</p>
  {CSW_TABLE}
</section>

<section id="issues">
  <p class="eyebrow">확인 필요 사항</p>
  <h2>확정 전에 정리할 쟁점</h2>
  {issues_table()}
</section>

<section id="refs">
  <p class="eyebrow">근거</p>
  <h2>근거 문서</h2>
  {refs_table()}
  <p class="note-box">제품 사양·가격 출처는 존 HW·존 SW·셀 HW·셀 SW 표의 ‘출처’ 열에 링크로 달았음.</p>
</section>
</main>
<script>
(function(){{
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function flash(id){{
    var els = [];
    if (id.indexOf('topo-') === 0) {{
      els = Array.prototype.slice.call(document.querySelectorAll('[data-node="' + id.slice(5) + '"]'));
    }} else {{
      var el = document.getElementById(id); if (el) els = [el];
    }}
    els.forEach(function(n){{ n.classList.add('flash'); }});
  }}
  function clearFlash(){{
    Array.prototype.forEach.call(document.querySelectorAll('.flash'), function(n){{ n.classList.remove('flash'); }});
  }}
  document.addEventListener('click', function(e){{
    clearFlash();  /* 강조는 다음 마우스 클릭으로만 해제 */
    var a = e.target.closest && e.target.closest('a[href^="#hw-"], a[href^="#sw-"], a[href^="#chw-"], a[href^="#csw-"], a[href^="#topo-"], a[href="#hw"], a[href="#sw"], a[href="#chw"], a[href="#csw"]');
    if (!a) return;
    var id = a.getAttribute('href').slice(1);
    var target = document.getElementById(id);
    if (!target) return;
    e.preventDefault();
    target.scrollIntoView({{behavior: reduce ? 'auto' : 'smooth', block: 'center'}});
    var lst = a.getAttribute('data-flash');
    if (lst) {{ lst.split(',').forEach(function(x){{ flash(x); }}); }} else {{ flash(id); }}
    try {{ history.replaceState(null, '', '#' + id); }} catch (err) {{}}
  }});
}})();
</script>
'''


if __name__ == "__main__":
    open(out("ocs_precision.html"), "w", encoding="utf-8").write(page())
    print('ok', round(MONTH_TB, 1), round(NEED_TB), N_STO)
