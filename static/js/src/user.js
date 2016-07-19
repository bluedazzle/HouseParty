/**
 * Created by RaPoSpectre on 4/28/16.
 */

Vue.config.delimiters = ['${', '}}'];
new Vue({
    el: '#vUsers',
    data: {
        query: ''
    },
    methods: {
        getData: function (event, page) {
            if (page == undefined) {
                return 0;
            }
            this.$set('users', null);
            var url = '';
            if (this.query == '') {
                url = generateUrlWithToken('admin/api/users') + '&page=' + page.toString();
            } else {
                url = generateUrlWithToken('admin/api/users') + '&page=' + page.toString() + '&query=' + this.query;
            }
            this.$http.get(url, function (data) {
                if (data.status == 1) {
                    this.$set('users', data.body.partyuser_list);
                    this.$set('pageObj', data.body.page_obj)
                } else if (data.status == 3) {
                    window.location.href = '/admin/login';
                }
            })
        },
        forbidUser: function (id) {
            url = generateUrlWithToken('admin/api/user/' + id + '/forbid', getCookie('token'));
            this.$http.post(url, {}, function (data) {
                if (data.status == 1) {
                    $.scojs_message('操作成功', $.scojs_message.TYPE_OK);
                    this.getData(null, 1);
                } else {
                    $.scojs_message('操作失败', $.scojs_message.TYPE_ERROR);
                }
            })
        }
    },
    ready: function () {
        this.getData(null, 1);
    },
    computed: {
        noData: function () {
            return this.users == null;
        }
    }
});
