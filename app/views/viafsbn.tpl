<div id="sbn_found">
    Informazioni sul record di autorità {{tipo}} n. <a href="{{item.url}}">{{item.code}}</a><br />
    Nome:  {{item.name}}<br />

    % if tipo == "VIAF":
        <strong>Collegamenti</strong>
        <ul>
        % for k, v in vars(item.links).iteritems():
            <li>{{k}}: {{v}}
        %end
    %end
</div>