import blenderproc as bproc
import numpy as np
import argparse
import os

# 커맨드 라인 인자
parser = argparse.ArgumentParser(description='BlenderProc 고급 실습')
parser.add_argument('--num_frames', type=int, default=100, help='생성할 프레임 수')
parser.add_argument('--output_dir', type=str, default='output/advanced_dataset', help='출력 디렉토리')
args = parser.parse_args()

print("=" * 50)
print("BlenderProc 고급 실습")
print("로봇 비전 데이터셋 구축")
print("=" * 50)
print(f"프레임 수: {args.num_frames}")
print(f"출력 디렉토리: {args.output_dir}")
print()

# ====================================
# 1. BlenderProc 초기화
# ====================================
print("[Step 1] BlenderProc 초기화 중...")
bproc.init()
print("✓ BlenderProc 초기화 완료")

# ====================================
# 2. 조명 설정 (고급 3-point lighting)
# ====================================
print("[Step 2] 고급 조명 시스템 구성 중...")

# Key Light (주 조명)
key_light = bproc.types.Light()
key_light.set_type("SUN")
key_light.set_energy(5)
key_light.set_location([5, -5, 10])
key_light.set_rotation_euler([-0.785, 0, -0.785])  # -45도, 0, -45도

# Fill Light (보조 조명)
fill_light = bproc.types.Light()
fill_light.set_type("SUN")
fill_light.set_energy(2)
fill_light.set_location([-5, 5, 8])
fill_light.set_rotation_euler([-0.611, 0, 0.785])  # -35도, 0, 45도

# Back/Rim Light (윤곽 조명)
rim_light = bproc.types.Light()
rim_light.set_type("SUN")
rim_light.set_energy(1.5)
rim_light.set_location([0, 5, 5])
rim_light.set_rotation_euler([0, 0, 0])

print("✓ 3-point 조명 시스템 완료")

# ====================================
# 3. 환경 구성
# ====================================
print("[Step 3] 환경 구성 중...")

# 지면
ground = bproc.object.create_primitive('PLANE', scale=[10, 10, 1])
ground.set_location([0, 0, 0])
ground.set_name("ground_plane")
ground.set_cp("category_id", 0)  # 배경 클래스

# 지면에 재질 추가
ground_mat = bproc.material.create('ground_material')
ground_mat.set_principled_shader_value("Base Color", [0.8, 0.8, 0.8, 1.0])
ground_mat.set_principled_shader_value("Roughness", 0.8)
ground.replace_materials(ground_mat)

# 테이블 (작업 공간)
table = bproc.object.create_primitive('CUBE', scale=[0.8, 0.8, 0.05])
table.set_location([0.5, 0.0, 0.35])
table.set_name("table")
table.set_cp("category_id", 0)  # 배경 클래스

# 테이블에 재질 추가
table_mat = bproc.material.create('table_material')
table_mat.set_principled_shader_value("Base Color", [0.5, 0.5, 0.5, 1.0])
table_mat.set_principled_shader_value("Roughness", 0.5)
table.replace_materials(table_mat)

# 테이블을 고정 객체로 설정
table.enable_rigidbody(False, friction=0.5, collision_shape='BOX')

print("✓ 환경 구성 완료")

# ====================================
# 4. YCB 객체 로드
# ====================================
print("[Step 4] YCB 객체 로드 중...")

# YCB 객체 정의 (BOP 데이터셋의 YCB-Video 사용)
ycb_objects_info = [
    {"name": "potted_meat_can", "obj_id": 10, "position": [0.5, 0.0, 0.45]},
    {"name": "banana", "obj_id": 11, "position": [0.4, 0.15, 0.45]},
    {"name": "large_marker", "obj_id": 40, "position": [0.6, -0.15, 0.45]},
    {"name": "tomato_soup_can", "obj_id": 5, "position": [0.35, -0.1, 0.45]},
]

# YCB-V 데이터셋 다운로드 경로 (BOP 형식)
# 실제 사용시에는 bproc.loader.load_bop_objs를 사용
# 여기서는 간단한 프리미티브로 대체
ycb_objects = []

for i, obj_info in enumerate(ycb_objects_info):
    # 프리미티브로 YCB 객체 시뮬레이션 (실제로는 BOP 데이터셋 사용)
    if "can" in obj_info["name"]:
        obj = bproc.object.create_primitive('CYLINDER', scale=[0.03, 0.03, 0.06], radius=1.0)
    elif "banana" in obj_info["name"]:
        obj = bproc.object.create_primitive('CYLINDER', scale=[0.025, 0.025, 0.1], radius=1.0)
    elif "marker" in obj_info["name"]:
        obj = bproc.object.create_primitive('CYLINDER', scale=[0.015, 0.015, 0.08], radius=1.0)
    else:
        obj = bproc.object.create_primitive('CUBE', scale=[0.05, 0.05, 0.05])
    
    obj.set_location(obj_info["position"])
    obj.set_name(obj_info["name"])
    
    # 카테고리 설정 (세그멘테이션용)
    obj.set_cp("category_id", i + 1)
    
    # 재질 추가
    mat = bproc.material.create(f'{obj_info["name"]}_material')
    # 각 객체마다 다른 색상
    colors = [
        [0.8, 0.2, 0.2, 1.0],  # 빨강
        [0.9, 0.9, 0.2, 1.0],  # 노랑
        [0.2, 0.2, 0.8, 1.0],  # 파랑
        [0.8, 0.4, 0.2, 1.0],  # 주황
    ]
    mat.set_principled_shader_value("Base Color", colors[i])
    mat.set_principled_shader_value("Roughness", 0.6)
    mat.set_principled_shader_value("Metallic", 0.1)
    obj.replace_materials(mat)
    
    # 물리 속성 활성화
    obj.enable_rigidbody(True, mass=0.1, friction=0.5, collision_shape='CONVEX_HULL')
    
    ycb_objects.append(obj)
    print(f"  ✓ {obj_info['name']} 생성 완료")

print("✓ YCB 객체 로드 완료")

# ====================================
# 5. 다중 카메라 설정
# ====================================
print("[Step 5] 다중 카메라 시스템 구성 중...")

# 카메라 내부 파라미터 설정
bproc.camera.set_resolution(512, 512)

# 메인 카메라 위치들 (다양한 뷰포인트)
# 구형 샘플링을 위한 카메라 포즈들
camera_poses = []

print("✓ 카메라 시스템 구성 완료")

# ====================================
# 6. 도메인 랜덤화 설정
# ====================================
print("[Step 6] 도메인 랜덤화 설정 중...")

# 각 프레임마다 적용될 랜덤화 함수
def randomize_scene():
    """씬의 다양한 속성을 랜덤화"""
    
    # 1. 객체 위치 랜덤화
    for obj in ycb_objects:
        obj.set_location([
            np.random.uniform(0.3, 0.7),  # x
            np.random.uniform(-0.25, 0.25),  # y
            np.random.uniform(0.42, 0.5)  # z
        ])
        # 회전 랜덤화
        obj.set_rotation_euler([
            np.random.uniform(0, 2 * np.pi),
            np.random.uniform(0, 2 * np.pi),
            np.random.uniform(0, 2 * np.pi)
        ])
    
    # 2. 조명 강도 랜덤화
    key_light.set_energy(np.random.uniform(3, 7))
    fill_light.set_energy(np.random.uniform(1, 3))
    rim_light.set_energy(np.random.uniform(0.5, 2))
    
    # 3. 테이블 색상 랜덤화
    random_color = np.random.uniform(0.3, 0.8, size=3).tolist() + [1.0]
    table_mat.set_principled_shader_value("Base Color", random_color)
    
    # 4. 배경 색상 랜덤화
    random_bg_color = np.random.uniform(0.3, 0.8, size=3).tolist() + [1.0]
    ground_mat.set_principled_shader_value("Base Color", random_bg_color)

print("✓ 도메인 랜덤화 설정 완료")

# ====================================
# 7. 렌더링 설정
# ====================================
print("[Step 7] 렌더링 설정 중...")

# 렌더링 품질 설정
bproc.renderer.set_max_amount_of_samples(256)
bproc.renderer.set_noise_threshold(0.01)
# denoiser는 환경에 따라 지원 여부가 다르므로 생략

# 출력 데이터 활성화
bproc.renderer.enable_normals_output()
bproc.renderer.enable_depth_output(activate_antialiasing=False)
bproc.renderer.enable_segmentation_output(map_by=["category_id", "instance", "name"])

print("✓ 렌더링 설정 완료")

# ====================================
# 8. 데이터 생성 루프
# ====================================
print(f"\n{'='*50}")
print("[고급 데이터셋 생성 시작]")
print("="*50)
print(f"총 {args.num_frames}개의 프레임을 생성합니다...")

import time
start_time = time.time()

for frame_idx in range(args.num_frames):
    # 씬 랜덤화
    randomize_scene()
    
    # 물리 시뮬레이션 안정화 (선택적)
    if frame_idx % 10 == 0:
        bproc.object.simulate_physics_and_fix_final_poses(
            min_simulation_time=0.5,
            max_simulation_time=2,
            check_object_interval=0.1
        )
    
    # 카메라 포즈 샘플링 (구형 샘플링)
    # 메인 뷰
    location_main = np.array([
        np.random.uniform(0.8, 1.4),
        np.random.uniform(0.8, 1.4),
        np.random.uniform(0.6, 1.2)
    ])
    rotation_matrix_main = bproc.camera.rotation_from_forward_vec(
        np.array([0.5, 0.0, 0.45]) - location_main,
        inplane_rot=np.random.uniform(0, 2 * np.pi)
    )
    cam2world_main = bproc.math.build_transformation_mat(location_main, rotation_matrix_main)
    
    # 탑뷰
    location_top = np.array([0.5, 0.0, 1.5])
    rotation_matrix_top = bproc.camera.rotation_from_forward_vec(
        np.array([0, 0, -1])  # 아래를 향함
    )
    cam2world_top = bproc.math.build_transformation_mat(location_top, rotation_matrix_top)
    
    # 사이드뷰
    location_side = np.array([1.5, 0.0, 0.6])
    rotation_matrix_side = bproc.camera.rotation_from_forward_vec(
        np.array([0.5, 0.0, 0.45]) - location_side
    )
    cam2world_side = bproc.math.build_transformation_mat(location_side, rotation_matrix_side)
    
    # 3개의 카메라 포즈 추가
    bproc.camera.add_camera_pose(cam2world_main)
    bproc.camera.add_camera_pose(cam2world_top)
    bproc.camera.add_camera_pose(cam2world_side)
    
    # 진행상황 표시
    if (frame_idx + 1) % 10 == 0 or frame_idx == 0:
        print(f"  프레임 {frame_idx + 1}/{args.num_frames} 설정 완료")

end_time = time.time()
setup_time = end_time - start_time

print(f"✓ 카메라 포즈 설정 완료 ({setup_time:.2f}초)")

# ====================================
# 9. 렌더링 및 저장
# ====================================
print(f"\n{'='*50}")
print("[렌더링 시작]")
print("="*50)

render_start = time.time()

# 렌더링 실행
data = bproc.renderer.render()

render_end = time.time()
render_time = render_end - render_start

print(f"✓ 렌더링 완료 ({render_time:.2f}초)")

# ====================================
# 10. 데이터 저장
# ====================================
print("[Step 10] 데이터 저장 중...")

# COCO 형식으로 저장 (2D Bounding Box, Segmentation)
bproc.writer.write_coco_annotations(
    os.path.join(args.output_dir, 'coco_data'),
    instance_segmaps=data["instance_segmaps"],
    instance_attribute_maps=data["instance_attribute_maps"],
    colors=data["colors"],
    color_file_format="PNG",
    append_to_existing_output=True
)

# HDF5 형식으로 저장 (모든 데이터)
bproc.writer.write_hdf5(
    os.path.join(args.output_dir, 'hdf5_data'),
    data,
    append_to_existing_output=True
)

save_time = time.time() - render_end

print(f"✓ 데이터 저장 완료 ({save_time:.2f}초)")
print(f"  - COCO 형식: {os.path.join(args.output_dir, 'coco_data')}")
print(f"  - HDF5 형식: {os.path.join(args.output_dir, 'hdf5_data')}")

# ====================================
# 11. 결과 요약
# ====================================
total_time = time.time() - start_time

print(f"\n{'='*50}")
print("[데이터 생성 완료]")
print("="*50)

print(f"✓ 생성된 프레임: {args.num_frames} (각 프레임당 3개 뷰포인트)")
print(f"✓ 총 이미지: {args.num_frames * 3}개")
print(f"✓ 설정 시간: {setup_time:.2f}초")
print(f"✓ 렌더링 시간: {render_time:.2f}초")
print(f"✓ 저장 시간: {save_time:.2f}초")
print(f"✓ 총 소요 시간: {total_time:.2f}초")
print(f"✓ 평균 렌더링 속도: {(args.num_frames * 3) / render_time:.2f} FPS")

print("\n✓ 프로그램 종료")