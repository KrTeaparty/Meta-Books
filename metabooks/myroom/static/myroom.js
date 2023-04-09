import * as THREE from "three";
import { OrbitControls } from "OrbitControls";
import { RGBELoader } from "RGBELoader";

class App {
  constructor() {
    const divContainer = document.querySelector("#webgl-container");
    this._divContainer = divContainer;

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    divContainer.appendChild(renderer.domElement);

    this._renderer = renderer;

    //toneMapping
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1;

    const scene = new THREE.Scene();
    this._scene = scene;

    this._setupCamera();
    this._setupLight();
    this._setupModel();
    this._setupControls();
    this._setupBackground();

    window.onresize = this.resize.bind(this);
    this.resize();

    requestAnimationFrame(this.render.bind(this));
  }

  _setupControls() {
    this._controls = new OrbitControls(this._camera, this._divContainer);
  }
  _setupCamera() {
    const width = this._divContainer.clientWidth;
    const height = this._divContainer.clientHeight;
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 100);
    camera.position.z = 4;
    this._camera = camera;
  }

  // hdr 파일 교체 예정
  _setupBackground() {
    new RGBELoader().load(
      "/metabooks/myroom/static/src/neon_photostudio_4k.hdr",
      (texture) => {
        texture.mapping = THREE.EquirectangularReflectionMapping;
        this._scene.background = texture;
        this._scene.environment = texture;
      }
    );
  }
  _setupLight() {
    // const color = 0xffffff;
    // const intensity = 1;
    // const light = new THREE.DirectionalLight(color, intensity);
    // light.position.set(-1, 2, 4);
    // this._scene.add(light);
  }

  _setupModel() {
    const geometry = new THREE.TorusKnotGeometry(1, 0.3, 256, 64, 2, 3);
    const material = new THREE.MeshStandardMaterial({ color: 0xffffff });

    const cube = new THREE.Mesh(geometry, material);

    this._scene.add(cube);
    this._cube = cube;
  }

  resize() {
    const width = this._divContainer.clientWidth;
    const height = this._divContainer.clientHeight;

    this._camera.aspect = width / height;
    this._camera.updateProjectionMatrix();

    this._renderer.setSize(width, height);
  }

  render(time) {
    this._renderer.render(this._scene, this._camera);
    this.update(time);
    requestAnimationFrame(this.render.bind(this));
  }

  update(time) {
    time *= 0.001;

    this._controls.update();
  }
}

window.onload = function () {
  new App();
};
