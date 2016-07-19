/**
 * Created by RaPoSpectre on 4/20/16.
 */

Vue.config.delimiters = ['${', '}}'];

new Vue({
    el: '#vLogin',
    data: {
        login_dict: {
            username: '',
            password: ''
        },
        res: {
            username: null,
            password: null
        },
        isLogin: false
    },

    methods: {
        login: function (event) {
            this.isLogin = true;
            url = generateUrl('admin/api/login');
            this.$http.post(url, this.login_dict, function (data) {
                if(data.status != 1){
                    this.$set('res', data.msg);
                    this.isLogin = false;
                }else {
                    setCookie('token', data.body.token);
                    window.location.href = '/admin/index'
                }
            })
        },
        change: function (event) {
            var name = event.target.name;
            if(name == "username"){
                this.res.username = null;
            }else{
                this.res.password = null;
            }
        }
    },

    computed: {
        usernameError: function () {
            if(this.res.username != null){
                return true;
            }else{
                return false;
            }
        },

        passwordError: function () {
            if(this.res.password != null){
                return true;
            }else{
                return false;
            }
        },

        test: function (){
            return true;
        }
    }
});