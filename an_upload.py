# -*- coding: utf-8 -*-
import wuy

class index(wuy.Window):
    """
    <script>
    function mydragover(e) {
        e.target.style.background = "red";
        e.preventDefault()
    }
    function mydragend(e) {
        e.target.style.background = "white";
    }
    function mydrop(e) {
        e.target.style.background = "white";
        for(var f of e.dataTransfer.files) {
            var reader = new FileReader();
            reader.onload = function (ee) {
                wuy.upload(f.name,ee.target.result)
            };
            // reader.readAsDataURL(f);
            reader.readAsText(f);
        }
        e.preventDefault()
    }
    </script>
    <body
        ondragover="mydragover(event)"
        ondragleave="mydragend(event)"
        ondragend="mydragend(event)"
        ondrop="mydrop(event)">drop on me</body>
    """

    def upload(self,name,content):
        # here, on server side : save the file 'name', with the text 'content',
        print("server:",name,content)

if __name__=="__main__":
    index()
