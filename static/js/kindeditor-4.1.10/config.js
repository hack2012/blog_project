KindEditor.ready(function (K) {
    K.create('textarea[name=content]', {
        width: '700px',
        height: '300px',
        // resizeType: 0,
        // allowImageRemote: false,
        // allowPreviewEmoticons: false,
        uploadJson: '/admin/upload/kindeditor',
    });
});