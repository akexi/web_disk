document.getElementById('uploadBtn')?.addEventListener('click', function() {
  document.getElementById('fileInput').click();
});

document.getElementById('fileInput')?.addEventListener('change', function() {
  const fd = new FormData();
  for (let f of this.files) fd.append('files', f);
  fd.append('parent_id', '{{ parent_id }}');

  // 显示进度条容器
  const progressBarContainer = document.getElementById('progressBarContainer');
  progressBarContainer.style.display = 'block';

  const xhr = new XMLHttpRequest();
  xhr.open('POST', '{{ url_for("upload") }}');

  // 监听上传进度
  xhr.upload.onprogress = function(e) {
    if (e.lengthComputable) {
      const percent = Math.floor((e.loaded / e.total) * 100);
      document.querySelector('.progress-bar').style.width = percent + '%';
      document.querySelector('.progress-bar').setAttribute('aria-valuenow', percent);
    }
  };

  // 上传完成后处理
  xhr.onload = function() {
    // 隐藏进度条
    progressBarContainer.style.display = 'none';

    if (xhr.status === 200) {
      // 显示上传成功的弹窗
      const modal = new bootstrap.Modal(document.getElementById('uploadSuccessModal'));
      modal.show();

      // 上传完成后，刷新页面
      location.reload();
    } else {
      alert("文件上传失败，请重试。");
    }
  };

  xhr.send(fd);
});
