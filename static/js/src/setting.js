/**
 * Created by RaPoSpectre on 5/10/16.
 */

Vue.config.delimiters = ['${', '}}'];
new Vue({
    el: '#vSetting',
    data: {
        modify: {
            new_password: '',
            old_password: ''
        }
    },
    methods: {
        changePassword: function () {
            var url = generateUrlWithToken('admin/api/admin', getCookie('token'));
            this.$http.post(url, this.modify, function(data){
                if(data.status==1){
                    $.scojs_message('管理密码修改成功', $.scojs_message.TYPE_OK);
                    this.modify.new_password = '';
                    this.modify.old_password = '';
                }else{
                    $.scojs_message('修改失败:' + data.msg, $.scojs_message.TYPE_ERROR);
                }
            })
        }
    },
    ready: function() {
        url = generateUrlWithToken('admin/api/admin', getCookie('token'));
        this.$http.get(url, function (data) {
            if (data.status == 1) {
                this.$set('admin', data.body);
            }
        })
    },
    computed: {}
});

